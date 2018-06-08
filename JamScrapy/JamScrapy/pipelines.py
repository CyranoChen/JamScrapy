# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from JamScrapy import config
from JamScrapy.mysql import MySQL

from sqlalchemy import create_engine


class JamScrapyPipeline(object):
    def process_item(self, item, spider):
        if spider.name == 'JamSearchSpider':
            return self.__process_jam_search_spider(item)
        elif spider.name == 'JamPostSpider':
            return self.__process_jam_post_spider(item)
        elif spider.name == 'JamProfileSpider':
            return self.__process_jam_profile_spider(item)
        elif spider.name == 'JamProfileGroupSpider':
            return self.__process_jam_profile_group_spider(item)
        elif spider.name == 'JamProfileFollowSpider':
            return self.__process_jam_profile_follow_spider(item)
        elif spider.name == 'PortalProfileSpider':
            return self.__process_portal_profile_spider(item)

    def __process_jam_search_spider(self, item):
        urls = []
        for url in item['topics']:
            urls.append('http://' + config.DOMAIN + url)

        item['topics'] = urls

        # print(item["url"], item["topics"])

        # Connect to the database
        db = MySQL()

        para = [db.escape_string(str(item["url"])),
                db.escape_string(str(item["body"])),
                db.escape_string(str(item["topics"]))]
                #db.escape_string(str(item['id']))]

        sql = f'insert into spider_jam_search (url, body, topics, createtime, keyword) ' \
               f'values ("{para[0]}", "{para[1]}", "{para[2]}", NOW(), "{config.KEYWORD}")'

        #sql = f'update spider_jam_search set body="{para[1]}", topics="{para[2]}", createtime=NOW() where id = {para[3]}'

        db.query(sql)

        return item


    def __process_jam_post_spider(self, item):
        # Connect to the database
        db = MySQL()

        para = [db.escape_string(str(item["baseurl"])),
                db.escape_string(str(item["url"])),
                db.escape_string(str(item["body"]))]
                #db.escape_string(str(item['id']))]

        sql = f'insert into spider_jam_post (baseurl, url, body, createtime, keyword) ' \
              f'values ("{para[0]}", "{para[1]}", "{para[2]}", NOW(), "{config.KEYWORD}")'

        #sql = f'update spider_jam_post set body="{para[2]}", createtime=NOW() where id = {para[3]}'

        # print(item["url"])

        result = db.query(sql)

        return item

    def __process_jam_profile_spider(self, item):
        # Connect to the database
        db = MySQL()

        para = [db.escape_string(str(item["peoplename"])),
                db.escape_string(str(item["url"])),
                db.escape_string(str(item["body"]))]

        sql = f'insert into spider_jam_profile(peoplename, url, body, createtime, keyword) ' \
              f'values ("{para[0]}", "{para[1]}", "{para[2]}", NOW(), "blockchain")'

        result = db.query(sql)

        return item

    def __process_jam_profile_group_spider(self, item):
        db = MySQL()

        if 'groups' in item.keys():
            para = [str(item["id"]), db.escape_string(str(item["groups"]))]

            sql = f'update jam_profile set groups="{para[1]}" where id = {para[0]}'

            result = db.query(sql)

        return item

    def __process_jam_profile_follow_spider(self, item):
        db = MySQL()

        if 'followers' in item.keys():
            sql = f'update jam_profile set followers="{db.escape_string(str(item["followers"]))}" where id = {str(item["id"])}'
            result = db.query(sql)

        if 'following' in item.keys():
            sql = f'update jam_profile set following="{db.escape_string(str(item["following"]))}" where id = {str(item["id"])}'
            result = db.query(sql)

        return item

    def __process_portal_profile_spider(self, item):
        # Connect to the database
        db = MySQL()

        para = [db.escape_string(str(item["username"])),
                db.escape_string(str(item["url"])),
                db.escape_string(str(item["body"]))]

        sql = f'insert into portal_profile_spider(username,url,body,createtime) values ("{para[0]}","{para[1]}","{para[2]}",NOW())'
        result = db.query(sql)

        return item
