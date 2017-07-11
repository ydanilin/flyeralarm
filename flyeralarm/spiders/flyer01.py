# -*- coding: utf-8 -*-
import re
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

        item = Product()
        # TODO extract SKU
        # process breadcrumbs
        bread = response.css('nav.breadcrumbs')
        if bread:
            a = bread.xpath('(.//a)[last()]')
            if a:
                groupName = a.xpath('./@title').extract_first().strip()
                groupPage = a.xpath('./@href').extract_first().strip()
                if groupName != 'Start':
                    item['groupName'] = groupName
                    item['groupPage'] = response.urljoin(groupPage)
        # process name
        name = response.css('h1.productName').xpath('./text()').extract_first().strip()
        item['name'] = name
        item['page'] = response.url
        # go for ajax
        attrs = response.xpath('//li[contains(@id, "productgroupAttribute")]')
        for attr in attrs:
            aName = ' '.join(attr.xpath('./text()').extract_first().split())
            aName = aName[aName.index(' ')+1:]
            print(aName)

        avDivs = response.xpath('//div[contains(@onclick, "selectShoppingCartAttribute")]')
        for a in avDivs:
            # inspect_response(response, self)
            av = a.xpath('./@onclick').extract_first()
            # (sku, attrID, valueID)
            avl = re.findall("\d+", av[av.index('(')+1:av.index(')')])
            print(avl)
            huj = a.css('div.attributeValueNameText').xpath('./text()').extract_first().strip()
            print(huj)
        return item
