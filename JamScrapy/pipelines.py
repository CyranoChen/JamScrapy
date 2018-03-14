# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from JamScrapy import config
from JamScrapy.mysql import MySQL


class JamScrapyPipeline(object):
    def process_item(self, item, spider):
        if spider.name == 'JamSearchSpider':
            return self.__process_jam_search_spider(item)
        elif spider.name == 'JamPostSpider':
            return self.__process_jam_post_spider(item)

    def __process_jam_search_spider(self, item):
        urls = []
        for url in item['topics']:
            urls.append('http://' + config.DOMAIN + url)

        item['topics'] = urls

        # Connect to the database
        db = MySQL()

        para = [db.escape_string(str(item["url"])),
                db.escape_string(str(item["body"])),
                db.escape_string(str(item["topics"]))]

        sql = f'insert into jam_search_spider(url,body,topics,createtime) values ("{para[0]}","{para[1]}","{para[2]}",NOW())'
        result = db.query(sql)

        return item

    def __process_jam_post_spider(self, item):
        db = MySQL()

        para = [str(item["id"]),
                db.escape_string(str(item["baseurl"])),
                db.escape_string(str(item["url"])),
                db.escape_string(str(item["body"]))]

        sql = f'update jam_post_spider set url="{para[2]}", body="{para[3]}", createtime=NOW() where id = {para[0]} AND baseurl = "{para[1]}"'

        #sql = f'insert into jam_post_spider(url,body,createtime) values ("{para[0]}","{para[1]}",NOW())'

        result = db.query(sql)

        return item
