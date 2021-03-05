import logging

import scrapy
from scrapy.pipelines.images import ImagesPipeline


class ImagesDownloadPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None, *, item=None):
        return request.meta['path']

    def get_media_requests(self, item, info):
        return scrapy.Request(item['url'], headers={
            'Referer': item['referer'],
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:85.0) Gecko/20100101 Firefox/85.0',
        }, meta=item)

    def item_completed(self, results, item, info):
        logging.info(results)
        logging.info(item)
        return item
