# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JamScrapyListItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    body = scrapy.Field()
    topics = scrapy.Field()


class JamScrapyPostItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    baseurl = scrapy.Field()
    url = scrapy.Field()
    body = scrapy.Field()
