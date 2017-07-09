# -*- coding: utf-8 -*-

import scrapy
from scrapy.downloadermiddlewares.retry import RetryMiddleware


class SupplierSpiderRetryMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        url = request.meta.get('splash', {}).get('args', {}).get('url', '')
        if url == spider.start_url:
            if spider.name == 'saxoprint':
                if not response.xpath('//div[@class="cbwh"]'):
                    reason = 'Missing product list container'
                    result = self._retry(request, reason, spider)
                    if not result:
                        raise scrapy.exceptions.IgnoreRequest()
                    return result
        return response
