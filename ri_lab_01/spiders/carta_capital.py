# -*- coding: utf-8 -*-
import scrapy
import json

from ri_lab_01.items import RiLab01Item
from ri_lab_01.items import RiLab01CommentItem
from datetime import datetime

class CartaCapitalSpider(scrapy.Spider):
    name = 'carta_capital'
    allowed_domains = ['cartacapital.com.br']
    start_urls = []
    count = 0

    def __init__(self, *a, **kw):
        super(CartaCapitalSpider, self).__init__(*a, **kw)
        with open('seeds/carta_capital.json') as json_file:
                data = json.load(json_file)
        self.start_urls = list(data.values())

    def parse(self, response):
        date = response.xpath("//meta[@property='article:published_time']/@content").get()
        if self.__isNoticePage(response) and self.___isNoticeYearAbove2018(date):
            yield self.__getNotice(response)

        visited = []
        for nextNotice in response.css('a::attr(href)').getall():
            if nextNotice is not None:
                if self.__validateLink(nextNotice) and visited.count(nextNotice) == 0:
                    # Contador de notícias válidas
                    self.count += 1
                    print(self.count)
                    yield scrapy.Request(nextNotice, callback=self.parse)
            visited.append(nextNotice)

        # page = response.url.split("/")[-2]
        # filename = 'quotes-%s.txt' % page
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log('Saved file %s' % filename)

    def __getNotice(self, response):
        return {
            'title': response.css('h1.eltdf-title-text::text').get(),
            "sub_title": response.css('div.wpb_wrapper h3::text').get(),
            'author': response.css('div.eltdf-title-post-author-info a::text').get(),
            'date': self.__formatDate(response.xpath("//meta[@property='article:published_time']/@content").get()),
            'section': response.css('div.eltdf-post-info-category a::text').get(),
            'text': "".join(response.css('article p::text').getall()),
            'url': response.request.url
        }

    def __isNoticePage(self, response):
        return response.css('article').get() is not None

    def __validateLink(self, link):
        for url in self.start_urls:
            if url.lower() in link.lower():
                return True

    def __formatDate(self, date):
        format = date.replace('T', ' ').split('+')[0]
        return datetime.strptime(format, '%Y-%m-%d %H:%M:%S')

    def ___isNoticeYearAbove2018(self, date):
        formatted = self.__formatDate(date)
        return formatted.year >= 2018

