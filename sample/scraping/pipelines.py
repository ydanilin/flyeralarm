# -*- coding: utf-8 -*-

import os
from scrapy.http import Request
from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.project import get_project_settings
from urllib.parse import urlparse, urljoin

from .items import SupplierProductItem


class ThumbnailPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        if isinstance(item, SupplierProductItem):
            proxy = get_project_settings().get('PROXY', os.getenv('PROXY'))
            URL = urlparse(item['URL'])
            baseURL = URL.scheme + '://' + URL.netloc
            return [Request(urljoin(baseURL, ''.join(x.split())),
                            meta={'proxy': proxy}) for x in
                    item.get(self.files_urls_field, []) if x and x != 'none']
