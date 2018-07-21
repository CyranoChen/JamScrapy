# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from JamScrapy import config
from JamScrapy.mysql import MySQL
from JamScrapy.entity import SpiderSearch, SpiderPost

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import datetime
import pymysql


class JamScrapyPipeline(object):
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

    def process_item(self, item, spider):
        if spider.name == 'JamSearchSpider' or spider.name == 'JamSearchPeopleSpider':
            return self.__process_jam_search_spider(item)
        elif spider.name == 'JamSearchFetchSpider':
            return self.__process_jam_search_fetch_spider(item)
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
        s = SpiderSearch()
        s.url = str(item['url'])
        s.body = str(item['body'])
        s.topics = str(item['topics'])
        s.createtime = datetime.datetime.now()
        s.keyword = config.KEYWORD

        session = sessionmaker(bind=self.engine)()
        session.add(s)
        session.commit()
        session.close()

        return item

    def __process_jam_search_fetch_spider(self, item):
        session = sessionmaker(bind=self.engine)()

        s = session.query(SpiderSearch).get(int(item['id']))

        if s:
            s.body = str(item['body'])
            s.topics = str(item['topics'])
            s.createtime = datetime.datetime.now()

            session.merge(s)
            session.commit()
        else:
            print(item['id'], item['url'])

        session.close()

        return item

    def __process_jam_post_spider(self, item):
        p = SpiderPost()
        p.baseurl = str(item['baseurl'])
        p.url = str(item['url'])
        p.body = str(item['body'])
        p.createtime = datetime.datetime.now()
        p.keyword = config.KEYWORD

        session = sessionmaker(bind=self.engine)()
        session.add(p)
        session.commit()
        session.close()

        return item

    def __process_jam_profile_spider(self, item):
        # engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        #
        # engine.execute(f'insert into spider_jam_profile(peoplename, url, body, createtime, keyword) '
        #                f'values ("{str(item["peoplename"])}", "{str(item["url"])}", "{str(item["body"])}", NOW(), "people")')

        # Connect to the database
        db = MySQL()

        para = [db.escape_string(str(item["peoplename"])),
                db.escape_string(str(item["url"])),
                db.escape_string(str(item["body"]))]

        sql = f'insert into spider_jam_profile (peoplename, url, body, createtime, keyword) ' \
              f'values ("{para[0]}", "{para[1]}", "{para[2]}", NOW(), "{config.KEYWORD}")'

        # sql = f'update spider_jam_post set body="{para[2]}", createtime=NOW() where id = {para[3]}'

        # print(item["url"])

        result = db.query(sql)

        return item

    def __process_jam_profile_group_spider(self, item):
        if 'groups' in item.keys() and item['groups'] is not None:
            engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
            engine.execute(f'update jam_profile set groups="{pymysql.escape_string(str(item["groups"]))}" where id = {item["id"]}')
        else:
            print('no groups:', item['username'])

        # db = MySQL()
        #
        # if 'groups' in item.keys():
        #     para = [str(item["id"]), db.escape_string(str(item["groups"]))]
        #
        #     sql = f'update jam_profile set groups="{para[1]}" where id = {para[0]}'
        #
        #     result = db.query(sql)

        return item

    def __process_jam_profile_follow_spider(self, item):
        db = MySQL()

        if 'followers' in item.keys():
            para = [db.escape_string(str(item["followers"])), db.escape_string(str(item["id"]))]
            sql = f'update jam_profile set followers="{para[0]}" where id = {para[1]}'
            db.query(sql)

        if 'following' in item.keys():
            para = [db.escape_string(str(item["following"])), db.escape_string(str(item["id"]))]
            sql = f'update jam_profile set following="{para[0]}" where id = {para[1]}'
            db.query(sql)

        # engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        #
        # if 'followers' in item.keys():
        #     sql = "update jam_profile set followers=:followers where id = :id"
        #     para = {"followers": str(item['followers']), "id": int(item['id'])}
        #     engine.execute(sql, para)
        #
        # if 'following' in item.keys():
        #     sql = "update jam_profile set following=:following where id = :id"
        #     para = {"following": str(item['following']), "id": int(item['id'])}
        #     engine.execute(sql, para)

        return item

    def __process_portal_profile_spider(self, item):
        # Connect to the database
        db = MySQL()

        para = [db.escape_string(str(item["username"])),
                db.escape_string(str(item["url"])),
                db.escape_string(str(item["body"]))]

        sql = f'insert into spider_portal_profile (username,url,body,createtime) values ("{para[0]}","{para[1]}","{para[2]}",NOW())'
        result = db.query(sql)

        return item
