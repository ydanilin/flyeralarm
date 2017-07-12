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
        # TODO extract SKU
        # process name
        name = response.css('h1.productName').xpath('./text()').extract_first().strip()
        item['name'] = name
        item['page'] = response.url
        # go for ajax
        attrs = response.xpath('//li[contains(@id, "productgroupAttribute")]')
        for attr in attrs:
            # attribute name
            aName = ' '.join(attr.xpath('./text()').extract_first().split())
            aName = aName[aName.index(' ')+1:]
            # print(aName)
        # attribute possible values
        avDivs = response.xpath('//div[contains(@onclick, "selectShoppingCartAttribute")]')
        for a in avDivs:
            # inspect_response(response, self)
            av = a.xpath('./@onclick').extract_first()
            # (sku, attrID, valueID)
            avl = re.findall("\d+", av[av.index('(')+1:av.index(')')])
            sku, aCode, aValCode = avl
            print(sku, aCode, aValCode)
            # attribute value
            huj = a.css('div.attributeValueNameText').xpath('./text()').extract_first().strip()
            print(huj)
            goNextAttr = '/uk/shop/configurator/selectattribute/id/{0}/width/0/height/0/{1}/{2}'.format(sku, aCode, aValCode)
            # goNextAttr = response.urljoin(goNextAttr)
            # print(goNextAttr)
            r = scrapy.Request(response.urljoin(goNextAttr), callback=self.parse_nextAttr)
            yield r
        return item

    def parse_nextAttr(self, response):
        html = json.loads(response.body)['configuratorContent']
        html = '<html><body>' + html + '</body></html>'
        sel = scrapy.selector.Selector(text=html)
        attrs = sel.xpath('//div[contains(@onclick, "selectShoppingCartAttribute")]/@onclick').extract()
        print(attrs)
        inspect_response(response, self)

