# Scrapy settings for the project

SPIDER_MODULES = ['project.spiders']
NEWSPIDER_MODULE = 'project.spiders'
DEFAULT_ITEM_CLASS = 'project.items.Product'

DOWNLOAD_DELAY = 0.5

ITEM_PIPELINES = {'project.pipelines.FilterPipeline': 1}
