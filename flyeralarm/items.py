# -*- coding: utf-8 -*-
import scrapy


class ProductItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    URL = scrapy.Field()
    data = scrapy.Field()
    parameters = scrapy.Field()


class AttribItem(scrapy.Item):
    name = scrapy.Field()
    data = scrapy.Field()
    values = scrapy.Field()


class ValueItem(scrapy.Item):
    name = scrapy.Field()
    data = scrapy.Field()



class SupplierProductItem(scrapy.Item):
    name = scrapy.Field()
    caption = scrapy.Field()
    URL = scrapy.Field()
    supplier = scrapy.Field()
    ''' data is an arbitrary supplier-specific data used to identify this
    product within supplier site when e.g. corresponding different
    translations'''
    data = scrapy.Field()

    def __repr__(self):
        return '<Product: ' + self.get('name', '(unknown)') + ' on ' + \
            str(self.get('supplier', '(unknown supplier)')) + '>'


class SupplierParameterItem(scrapy.Item):
    name = scrapy.Field()
    supplier = scrapy.Field()
    supplier_product = scrapy.Field()
    default_value = scrapy.Field()
    min_value = scrapy.Field()
    max_value = scrapy.Field()
    ''' data is an arbitrary supplier-specific data used to identify this
    parameter within supplier site when e.g. doing price scraping '''
    data = scrapy.Field()

    def __repr__(self):
        return '<Parameter: ' + self.get('name', '(unknown)') + ' of ' + \
            str(self.get('supplier_product', '(unknown)')) + ' on ' + \
            str(self.get('supplier', '(unknown supplier)')) + '>'


class SupplierValueItem(scrapy.Item):
    name = scrapy.Field()
    supplier_parameter = scrapy.Field()
    supplier = scrapy.Field()
    supplier_product = scrapy.Field()
    ''' data is an arbitrary supplier-specific data used to identify this value
     within supplier site when e.g. doing price scraping '''
    data = scrapy.Field()

    key = scrapy.Field()  # default/min/max

    def __repr__(self):
        return '<Value: ' + self.get('name', '(unknown)') + '>'
