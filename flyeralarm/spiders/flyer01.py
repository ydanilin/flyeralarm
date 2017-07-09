# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import Product


class Flyer01Spider(CrawlSpider):
    name = 'flyer01'
    allowed_domains = ['flyeralarm.com']
    start_urls = ['https://www.flyeralarm.com/uk/content/index/open/id/25414/all-products-a-z.html']
    rules = (
        Rule(LinkExtractor(restrict_css='div.productoverviewaz'), callback='parse_item'),
    )

    def parse_item(self, response):
        divRow = response.css('div.row')
        if divRow:
            for div in divRow[0].xpath('div'):
                link = div.xpath('.//a[1]/@href').extract_first()
                # https://stackoverflow.com/questions/13489473/how-can-i-extract-only-text-in-scrapy-selector-in-python
                name = div.xpath('.//span/text()').extract_first()
                # print(link, name)
                item = Product(dict(name=name, link=link))
                # item['link'] = link
                # item['name'] = name
                lnk = response.urljoin(link)
                request = scrapy.Request(lnk, callback=self.parse_details)
                request.meta['product'] = item
                return request

    def parse_details(self, response):
        item = response.meta['product']
        print(item['name'])
        print(item['link'])
        print(response.url)
        bread = response.css('nav.breadcrumbs')
        if bread:
            a = bread.xpath('(.//a)[last()]')
            groupUrl = a.xpath('./@href').extract_first().strip()
            groupName = a.xpath('./@title').extract_first().strip()
            print(groupUrl, groupName)
        from scrapy.shell import inspect_response
        inspect_response(response, self)

