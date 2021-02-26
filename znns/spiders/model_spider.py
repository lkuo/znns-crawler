import os

import scrapy
from znns.items import Model, Album

CAPTION_FILE_NAME = 'caption.jpg'


class ModelSpider(scrapy.Spider):
    name = 'models'

    def __init__(self):
        super(ModelSpider, self).__init__()
        self.albums = Album()
        self.models = Model()

    def start_requests(self):
        for model in self.models.list():
            yield scrapy.Request(model['url'], callback=self.parse, cb_kwargs=dict(model=model))

    def parse(self, response, **kwargs):
        model = kwargs['model']
        model_name, profile_url = self.get_model_detail(response)
        if model['name'] is None:
            self.models.update(model['id'], {'name': model_name})
        meta = {'model_id': model['id']}
        yield File(path=os.path.join('models', model['id'], CAPTION_FILE_NAME), url=profile_url, referer=response.url)

        if self.has_archive_more(response):
            yield response.follow(
                self.get_archive_more_url(response),
                self.parse_all_albums,
                cb_kwargs=dict(meta=meta))
        else:
            yield from self.parse_all_albums(response, meta)

    def parse_all_albums(self, response, meta):
        for cover, album_name, url in self.get_albums(response):
            if self.albums.has(url):
                continue
            album = self.albums.add(meta['model_id'], album_name, url)
            yield File(path=os.path.join('albums', album['id'], CAPTION_FILE_NAME), url=cover, referer=response.url)
            meta['album_id'] = album['id']
            yield response.follow(url, self.parse_album, cb_kwargs=dict(meta=meta))

        if self.has_albums_next_page(response):
            next_page_url = self.get_albums_next_page_url(response)
            yield response.follow(next_page_url, self.parse_all_albums, cb_kwargs=dict(meta=meta))

    def parse_album(self, response, meta):
        album_id = meta['album_id']

        for url in self.get_images(response):
            file_name = response.url.split('/')[-1]
            yield File(path=os.path.join('albums', album_id, file_name), url=url, referer=response.url)

        if self.has_album_next_page(response):
            next_page_url = self.get_album_next_page_url(response)
            yield response.follow(next_page_url, self.parse_album, cb_kwargs=dict(meta=meta))

    @staticmethod
    def get_model_detail(response):
        name = response.xpath('//h1/text()').get()
        profile_url = response.xpath('//div[@class="infoleft_imgdiv"]//img/@src').get()
        return name, profile_url

    @staticmethod
    def get_archive_more_url(response):
        return response.xpath('//span[@class="archive_more"]/a/@href').get()

    def has_archive_more(self, response):
        return self.get_archive_more_url(response) is not None

    @staticmethod
    def get_albums_next_page_url(response):
        return response.xpath('//div[@class="pagesYY"]//a[last()]/@href').get()

    def has_albums_next_page(self, response):
        return self.get_albums_next_page_url(response) is not None

    @staticmethod
    def get_albums(response):
        divs = response.xpath('//ul[@class="photo_ul"]/li[@class="igalleryli"]')
        for div in divs:
            cover = div.xpath('.//img/@data-original').get()
            if cover is None:
                cover = div.xpath('.//img/@src').get()
            album_name = div.xpath('.//a[@class="caption"]/text()').get()
            url = div.xpath('.//a[@class="igalleryli_link"]/@href').get()
            yield cover, album_name, url

    @staticmethod
    def get_images(response):
        return response.xpath('//ul[@id="hgallery"]/img/@src').getall()

    @staticmethod
    def get_album_next_page_url(response):
        return response.xpath('//div[@id="pages"]//a[last()]/@href').get()

    def has_album_next_page(self, response):
        next_page_url = self.get_album_next_page_url(response)
        return (next_page_url is not None) and ('htm' in next_page_url)


class File(scrapy.Item):
    path = scrapy.Field()
    url = scrapy.Field()
    referer = scrapy.Field()
