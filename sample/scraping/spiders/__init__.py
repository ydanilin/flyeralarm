#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :

import base64
from django.utils.text import slugify
import json
import os
from os.path import dirname, abspath, join
import scrapy
from scrapy_splash import SplashRequest
from tempfile import gettempdir

from ..items import SupplierProductItem, \
    SupplierParameterItem, SupplierValueItem


class SupplierSpider(scrapy.Spider):
    timeout = 30

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        script_name = self.script_name if hasattr(self, 'script_name') \
            else self.name
        with open(join(dirname(abspath(__file__)),
                       script_name + '.lua')) as script:
            self.script = script.read()
        self.product_script = self.script + ' main = scrape_product'

    def _dump_png(self, response, filename='dump'):
        data = response.data.get('png')
        if data:
            with open(join(gettempdir(), slugify(filename) + '.png'),
                      'wb') as f:
                f.write(base64.b64decode(data))

    def _dump_har(self, response, filename='dump'):
        data = response.data.get('har')
        if data:
            with open(join(gettempdir(), slugify(filename) + '.har'),
                      'w') as f:
                f.write(json.dumps(data))

    def _dump_html(self, response, filename='dump'):
        data = response.body
        if data:
            with open(join(gettempdir(), slugify(filename) + '.html'),
                      'wb') as f:
                f.write(data)

    def start_requests(self):
        self.proxy = self.settings.get('PROXY',
                                       os.getenv('PROXY', 'none'))
        if self.proxy != 'none':
            self.logger.info('Setting proxy to ' + self.proxy)
        yield SplashRequest(self.start_url, endpoint='execute',
                            cache_args=['lua_source'],
                            args={'lua_source': self.script,
                                  'proxy': self.proxy,
                                  'timeout': self.timeout})

    def parse_product(self, response):
        product = response.data.get('product')
        if not product:
            return

        self._dump_har(response, product.get('name', 'dump'))
        self._dump_png(response, product.get('name', 'dump'))

        parameters = product.pop('parameters', [])
        product_item = SupplierProductItem(product)
        yield product_item
        for parameter in parameters:
            parameter['supplier_product'] = product_item['name']
            values = parameter.pop('values', {})
            parameter_item = SupplierParameterItem(parameter)
            yield parameter_item
            for key, value in values.items():
                value['supplier_product'] = product_item['name']
                value['supplier_parameter'] = parameter_item['name']
                if not key.isnumeric():
                    value['key'] = key
                yield SupplierValueItem(value)
