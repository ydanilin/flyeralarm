# -*- coding: utf-8 -*-

import scrapy_splash


SPIDER_MODULES = ['scraping.spiders']
NEWSPIDER_MODULE = 'scraping.spiders'

BOT_NAME = 'pexxo'

LOG_LEVEL = 'INFO'

DUPEFILTER_DEBUG = True

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay  # noqa
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = True

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#     'Accept':
#         'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#     'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 200,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 300,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    'scraping.middlewares.SupplierSpiderRetryMiddleware': 560,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware':
        810,
    'scrapy.downloadermiddlewares.stats.DownloaderStats': 850,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
EXTENSIONS = {}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'scraping.pipelines.ThumbnailPipeline': 100,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings  # noqa
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
HTTPCACHE_DIR = '/var/cache/splash'

RETRY_TIMES = 4

# files pipeline settings
FILES_STORE = '/tmp'
FILES_URLS_FIELD = 'thumbnail_url'
FILES_RESULT_FIELD = 'thumbnail_file'
MEDIA_ALLOW_REDIRECTS = True

# Splash settings
SPLASH_URL = 'http://splash:8050'  # TODO : replace with splash address
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
SPLASH_SLOT_POLICY = scrapy_splash.SlotPolicy.SCRAPY_DEFAULT
# PROXY = 'socks5://tor:9050'

# fake-useragent settings
RANDOM_UA_TYPE = 'chrome'
RANDOM_UA_PER_PROXY = True
