# -*- coding: utf-8 -*-
import re
import json
from functools import reduce
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import ProductItem, AttribItem, ValueItem
from scrapy.shell import inspect_response


class Flyer01Spider(CrawlSpider):
    name = 'flyer01'
    allowed_domains = ['flyeralarm.com']
    start_urls = ['https://www.flyeralarm.com/uk/content/index/open/id/25414/all-products-a-z.html']
    rules = (
        # this rule extracts all product category links from "all categories" page
        Rule(LinkExtractor(restrict_css='div.productoverviewaz'), callback='parse_group'),
    )

    def __init__(self, *args, **kwargs):
        super(Flyer01Spider, self).__init__(*args, **kwargs)
        self.nextTemplate = ('/uk/shop/configurator/selectattribute'
                             '/id/{0}/width/0/height/0')

    def parse_group(self, response):
        isProduct = response.xpath('(//div[@id="shopWrapper"])[1]')
        isGroup = response.xpath('(//section[@id="openPage"])[1]')
        if isProduct:
            yield self.parse_details(response)
        elif isGroup:
            group = isGroup.xpath('.//div[@class="row"]')
            if group:
                # extracts links to individual product pages within the category
                for div in group.xpath('div'):
                    link = div.xpath('.//a[1]/@href').extract_first()
                    request = scrapy.Request(response.urljoin(link),
                                             callback=self.parse_group)
                    yield request
        else:
            print('Bad index page: neither prod nor group detected', response.url)

    def parse_details(self, response):
        # https://www.flyeralarm.com/uk/shop/configurator/index/id/6009/loyalty-cards.html
        isRecursive = response.meta.get('isRecursive', False)
        if not isRecursive:  # first time call
            name = response.css('h1.productName').xpath(
                './text()').extract_first().strip()
            url = response.url
            sku = re.search(r'\d+', url)
            item = ProductItem(dict(name=name,
                                    caption=name,
                                    supplier='Flyeralarm',
                                    URL=url,
                                    data=sku.group(),
                                    parameters=[])
                               )
            response.meta['goNextAttr'] = self.nextTemplate.format(item['data'])
            replacedResp = response
        else:  # if subsequent requests, pull cAttrDiv from json
            item = response.meta.get('item')
            html = json.loads(response.body)['configuratorContent']
            html = '<html><body>' + html + '</body></html>'
            replacedResp = scrapy.selector.Selector(text=html)

        # common part for both types of calls
        cAttrDiv = replacedResp.xpath('(//div[@id="currentAttribute"])[1]')
        values = self.parseAttributeValues(replacedResp)
        if (not cAttrDiv) or (not values['content']):  # termination condition
            return item
            # return
        aName = self.parseAttributeName(cAttrDiv)
        ai = AttribItem(dict(name=aName,
                             data=values['aid'],
                             supplier_product=item['name'],
                             values=[])
                        )
        item['parameters'].append(ai)
        for value in values['content']:
            vi = ValueItem(dict(name=value['valueName'],
                                supplier_parameter=value['attrName'],
                                data=value['attrValueID'],
                                supplier_product=item['name'])
                           )
            ai['values'].append(vi)
            self.crawler.stats.inc_value('attrs_scraped')

        # here the value id is taken from the last value !!
        goNextAttr = response.meta['goNextAttr'] + '/{0}/{1}'.format(
            values['aid'], values['vid'])
        request = scrapy.Request(response.urljoin(goNextAttr),
                                 callback=self.parse_details)
        request.meta['item'] = item
        request.meta['isRecursive'] = True
        request.meta['goNextAttr'] = goNextAttr
        return request
        # inspect_response(response, self)

    def parseAttributeValues(self, response):
        output = dict(aid=0, vid=0, content=[])
        valueDivs = []
        containerDiv = response.xpath('//div[@id = "attributeValues"]')
        if containerDiv:
            # every value block may be of class:
            # either "attributeValueContainer"
            # or "attributeValueList"
            # or "attributeValueTable"
            # also value text div class depends on it
            tryRecordClass = containerDiv.css('div.attributeValueContainer')
            if tryRecordClass:
                valueDivs = tryRecordClass
                valueTextClassName = "attributeValueNameText"
            else:
                tryRecordClass = containerDiv.css('div.attributeValueList')
                if tryRecordClass:
                    valueDivs = tryRecordClass
                    valueTextClassName = "attributeValueListNameText"
                else:
                    tryRecordClass = containerDiv.css('div.attributeValueTable')
                    if tryRecordClass:
                        valueDivs = tryRecordClass
                        valueTextClassName = "attributeValueTableName"

            for valueDiv in valueDivs:
                valueName = valueDiv.xpath('.//div[@class = $var]//text()',
                                           var=valueTextClassName).extract()
                valueName = reduce(lambda x, y: x + y, valueName).strip()
                jsProcName = valueDiv.xpath(
                    ('.//div[contains(@onclick, "selectShoppingCartAttribute")]'
                     '/@onclick')).extract_first()
                jsProcArgs = re.findall("\d+", jsProcName)
                output['aid'] = jsProcArgs[1]
                output['vid'] = jsProcArgs[2]
                output['content'].append(dict(sku=jsProcArgs[0],
                                              attrNameID=jsProcArgs[1],
                                              attrValueID=jsProcArgs[2],
                                              attrName='',
                                              valueName=valueName))
                # go for popup technical details if any
                id_ = 'attributeValueTechnicalDetail' + jsProcArgs[2]
                popupDiv = valueDiv.xpath('.//preceding-sibling::div[@id = $var]', var=id_)
                if popupDiv:
                    pairs = popupDiv.xpath('.//text()').extract()
                    pairs = list(filter(lambda x: x, map(lambda x: x.strip(), pairs)))
                    for pair in pairs:
                        nameAndValue = re.split(r':\s?', pair)
                        if len(nameAndValue) == 2:
                            output['content'].append(
                                dict(sku=jsProcArgs[0],
                                     attrNameID=0,
                                     attrValueID=0,
                                     attrName=nameAndValue[0],
                                     valueName=nameAndValue[1]))

        return output

    def parseAttributeName(self, aTag):
        output = ''
        tryTag = aTag.xpath('.//div[@id="selectedAttributeHeader"]/*[1]/text()')
        # tryTag = aTag.xpath('.//h3[1]/text()')
        if tryTag:
            output = ' '.join(aTag.xpath(
                './/div[@id="selectedAttributeHeader"]/*[1]/text()'
            ).extract_first().split())
            output = output[output.index(' ') + 1:]
        else:
            # log that's no attribute name
            pass
        return output
