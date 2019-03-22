# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JamScrapyGroupItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    url = scrapy.Field()
    body = scrapy.Field()
    groups = scrapy.Field()


class JamScrapySearchItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
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


class JamScrapyProfileItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    url = scrapy.Field()
    body = scrapy.Field()


class PortalScrapyProfileItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    username = scrapy.Field()
    url = scrapy.Field()
    body = scrapy.Field()


class JamScrapyProfileGroupItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    username = scrapy.Field()
    url = scrapy.Field()
    groups = scrapy.Field()


class JamScrapyProfileFollowItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    username = scrapy.Field()
    peoplename = scrapy.Field()
    url = scrapy.Field()
    followers = scrapy.Field()
    following = scrapy.Field()


class PortalSuccessFactorsItem(scrapy.Item):
    id = scrapy.Field()
    url = scrapy.Field()
    body = scrapy.Field()
