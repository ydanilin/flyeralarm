# -*- coding: utf-8 -*-
import re
import json
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import Product
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
            print('Eto product')
            yield self.parse_details(response)
        # if div class="contentProducts" - this is group page
        # section#openPage
        isGroup = response.css('div.contentProducts')
        if isGroup:
            print('Eto gruppa')
            group = isGroup.xpath('following-sibling::div[1]')
            if group:
                # extracts links to individual product pages within the category
                for div in group.xpath('div'):
                    link = div.xpath('.//a[1]/@href').extract_first()
                    request = scrapy.Request(response.urljoin(link),
                                             callback=self.parse_details)
                    yield request

    def parse_details(self, response):
        # https://www.flyeralarm.com/uk/shop/configurator/index/id/6009/loyalty-cards.html
        item = Product()
        print('parse_details')
        # TODO extract SKU
        # process name
        name = response.css('h1.productName').xpath('./text()').extract_first().strip()
        item['name'] = name
        item['page'] = response.url
        # go for attrs
        attrs = response.xpath('//li[contains(@id, "productgroupAttribute")]')
        attribOnPage = True
        for attr in attrs:
            aName = self.attributeName(attr)
            if 'delivery' in aName.lower():
                break
            if attribOnPage:
                attribOnPage = False
                values = self.parse_attrib_values(response)
                goNextAttr = ('/uk/shop/configurator/selectattribute'
                              '/id/{0}/width/0/height/0').format(values[-1]['sku'])
                print('first call', values, 'next url:', goNextAttr)
            else:
                goNextAttr += '/{0}/{1}'.format(values[-1]['attrNameID'],
                                                values[-1]['attrValueID'])
                r = scrapy.Request(response.urljoin(goNextAttr),
                                   callback=self.parse_nextAttr)
                yield r
                print('next call', values, 'next url:', goNextAttr)

    def parse_nextAttr(self, response):
        html = json.loads(response.body)['configuratorContent']
        html = '<html><body>' + html + '</body></html>'
        sel = scrapy.selector.Selector(text=html)
        values = self.parse_attrib_values(sel)
        # print('next call', values)
        yield values
        # inspect_response(response, self)

    def parse_attrib_values(self, response):
        output = []
        valueDivs = response.xpath('//div[contains(@onclick, "selectShoppingCartAttribute")]')
        for valueDiv in valueDivs:
            valueName = valueDiv.css('div.attributeValueNameText').xpath('./text()').extract_first().strip()
            jsProcName = valueDiv.xpath('./@onclick').extract_first()
            # (sku, attrID, valueID)
            jsProcArgs = re.findall("\d+", jsProcName)
            output.append(dict(sku=jsProcArgs[0],
                               attrNameID=jsProcArgs[1],
                               attrValueID=jsProcArgs[2],
                               valueName=valueName)
                          )
        return output

    def attributeName(self, aTag):
        name = ' '.join(aTag.xpath('./text()').extract_first().split())
        name = name[name.index(' ') + 1:]
        return name
