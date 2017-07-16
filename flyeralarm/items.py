# -*- coding: utf-8 -*-
import scrapy


class ProductItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    caption = scrapy.Field()
    supplier = scrapy.Field()
    URL = scrapy.Field()
    data = scrapy.Field()
    parameters = scrapy.Field()


class AttribItem(scrapy.Item):
    name = scrapy.Field()
    data = scrapy.Field()
    supplier_product = scrapy.Field()
    values = scrapy.Field()


class ValueItem(scrapy.Item):
    name = scrapy.Field()
    supplier_parameter = scrapy.Field()
    data = scrapy.Field()
    supplier_product = scrapy.Field()
