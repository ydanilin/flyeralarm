#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :

from scrapy_splash import SplashRequest

from . import SupplierSpider


class SaxoprintSpider(SupplierSpider):
    name = 'saxoprint'
    allowed_domains = ['saxoprint.de', 'saxoprint.co.uk']
    start_url = 'https://www.saxoprint.co.uk/productoverview'

    def _follow_item(self, response, item, headline=None, **kwargs):
        href = item.xpath('@href').extract_first()
        if not href:
            return
        URL = href.replace('\n', '')
        if not headline:
            headline = item.xpath(
                'p[@class="headline"]/text()[boolean(p[@class="headline"])]|'
                'text()[not(boolean(p[@class="headline"]))]').extract_first()
            headline = ' '.join((headline or '').split())
        args = {
            'lua_source': self.product_script,
            'proxy': self.proxy,
            'headline': headline
        }
        args.update(kwargs)
        return SplashRequest(response.urljoin(URL), self.parse_item,
                             endpoint='execute', cache_args=['lua_source'],
                             args=args)

    def parse(self, response):
        lst = response.xpath('//div[@class="cbwh"]//a')
        for item in lst:
            yield self._follow_item(response, item)

    def parse_item(self, response):
        if response.data.get('is_product_group'):
            if response.data.get('is_slider'):
                self.logger.info(str(response.request) + ': slider')
                categories = response.xpath('//div[@class="itemToShow"]')
                for category in categories:
                    for product in category.xpath('li'):
                        presentation = product.xpath(
                            'div[@class="itemPresentation"]')
                        if not presentation:
                            continue
                        button = presentation.xpath('div[@class="buttons"]')
                        if not button:
                            continue
                        yield self._follow_item(response, button)
            elif response.data.get('is_offergrid'):
                self.logger.info(str(response.request) + ': offergrid')
                grp = response.xpath('//ul[@class="offergrid"]/*/a')
                for item in grp:
                    yield self._follow_item(response, item)
            elif response.data.get('is_adjustable_group'):
                self.logger.info(str(response.request) + ': adjustable group')
                grp = response.xpath('//div[@class="cb"]/a')
                for item in grp:
                    yield self._follow_item(response, item)
            else:
                self.logger.info(str(response.request) + ': product group')
                grp = response.xpath('//div[@class="productlink"]//a')
                for item in grp:
                    yield self._follow_item(response, item)
        else:
            for item in self.parse_product(response):
                yield item
