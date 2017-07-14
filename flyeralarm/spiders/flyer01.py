# -*- coding: utf-8 -*-
import re
import json
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

    def parse_group(self, response):
        # if div id="shopWrapper" - this is an individual product page
        isProduct = response.xpath('(//div[@id="shopWrapper"])[1]')
        if isProduct:
            yield self.parse_details(response)
        isGroup = response.css('div.contentProducts')
        if isGroup:
            group = isGroup.xpath('following-sibling::div[1]')
            if group:
                # extracts links to individual product pages within the category
                for div in group.xpath('div'):
                    link = div.xpath('.//a[1]/@href').extract_first()
                    request = scrapy.Request(response.urljoin(link),
                                             callback=self.parse_group)
                    yield request

    def parse_details(self, response):
        # https://www.flyeralarm.com/uk/shop/configurator/index/id/6009/loyalty-cards.html
        isRecursive = response.meta.get('isRecursive', False)
        if not isRecursive:  # first time call
            name = response.css('h1.productName').xpath(
                './text()').extract_first().strip()
            url = response.url
            sku = re.search(r'\d+', url)
            item = ProductItem(dict(name=name, URL=url, data=sku.group(),
                                    parameters=[]))
            response.meta['goNextAttr'] = ('/uk/shop/configurator'
                                           '/selectattribute'
                                           '/id/{0}/width/0/height/0').format(
                item['data'])
            replacedResp = response
        else:  # if subsequent requests, pull cAttrDiv from json
            html = json.loads(response.body)['configuratorContent']
            html = '<html><body>' + html + '</body></html>'
            replacedResp = scrapy.selector.Selector(text=html)
            item = response.meta.get('item')

        # common part for both types of calls
        cAttrDiv = replacedResp.xpath('(//div[@id="currentAttribute"])[1]')
        if not cAttrDiv:  # termination condition
            return item
            # return
        values = self.parseAttributeValues(replacedResp)
        aName = self.parseAttributeName(cAttrDiv)
        ai = AttribItem(dict(name=aName,
                             data=values[-1]['attrNameID'],
                             values=[]))
        item['parameters'].append(ai)
        for value in values:
            vi = ValueItem(dict(name=value['valueName'],
                                data=value['attrValueID'])
                           )
            ai['values'].append(vi)
        # here the value id is taken from the last value !!
        goNextAttr = response.meta['goNextAttr'] + '/{0}/{1}'.format(
            ai['data'], vi['data'])
        request = scrapy.Request(response.urljoin(goNextAttr),
                                 callback=self.parse_details)
        request.meta['item'] = item
        request.meta['isRecursive'] = True
        request.meta['goNextAttr'] = goNextAttr
        return request
        # inspect_response(response, self)

    def parseAttributeValues(self, response):
        output = []
        valueDivs = []
        containerDiv = response.xpath('//div[@id = "attributeValues"]')
        if containerDiv:
            # every value block may be of class either "attributeValueContainer"
            # of "attributeValueList"
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

            for valueDiv in valueDivs:
                valueName = valueDiv.xpath('.//div[@class = $var]/text()',
                                           var=valueTextClassName).\
                    extract_first().strip()
                jsProcName = valueDiv.xpath(
                    ('.//div[contains(@onclick, "selectShoppingCartAttribute")]'
                     '/@onclick')).extract_first()
                jsProcArgs = re.findall("\d+", jsProcName)
                output.append(dict(sku=jsProcArgs[0],
                                   attrNameID=jsProcArgs[1],
                                   attrValueID=jsProcArgs[2],
                                   valueName=valueName))
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
