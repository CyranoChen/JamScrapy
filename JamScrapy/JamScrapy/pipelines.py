# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from JamScrapy import config
from JamScrapy.entity import SpiderSearch, SpiderPost, SpiderProfile, SpiderPortalProfile, SpiderGroup, SpiderComment

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import scrapy
import datetime


class JamScrapyPipeline(object):
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

    def process_item(self, item, spider):
        if spider.name == 'JamSearchSpider' or spider.name == 'JamGroupContentSpider':
            return self.__process_jam_search_spider(item)
        elif spider.name == 'JamSearchFetchSpider':
            return self.__process_jam_search_fetch_spider(item)
        elif spider.name == 'JamPostSpider':
            return self.__process_jam_post_spider(item)
        elif spider.name == 'JamProfileSpider' or spider.name == 'JamSearchPeopleSpider':
            return self.__process_jam_profile_spider(item)
        elif spider.name == 'JamProfileGroupSpider':
            return self.__process_jam_profile_group_spider(item)
        elif spider.name == 'JamProfileFollowSpider':
            return self.__process_jam_profile_follow_spider(item)
        elif spider.name == 'PortalProfileSpider':
            return self.__process_portal_profile_spider(item)
        elif spider.name == 'PortalProfileManagerSpider':
            return self.__process_portal_profile_manager_spider(item)
        elif spider.name == 'JamGroupSpider':
            return self.__process_jam_group_spider(item)
        elif spider.name == 'JamSearchCommentSpider':
            return self.__process_jam_comment_spider(item)
        elif spider.name == 'PortalSuccessFactorsSpider':
            return self.__process_portal_successfactors_spider(item)

    def __process_jam_search_spider(self, item):
        if 'request_access' not in str(item['url']) and len(item['topics']) > 0:
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

    def __process_jam_group_spider(self, item):
        groups = item['groups']

        if len(groups) > 0:
            session = sessionmaker(bind=self.engine)()

            for group in groups:
                html = scrapy.Selector(text=str(group))

                g = SpiderGroup()

                url = html.xpath('//div[@class="title"]/span/a/@href').extract()
                name = html.xpath('//div[@class="title"]/span/a/text()').extract()
                creator = html.xpath('//div[@class="meta"]/div[last()]/a/@href').extract()

                # print('name:', name)
                # print('creator', creator)

                if len(url) > 0:
                    g.groupurl = url[0].strip()
                else:
                    continue

                if len(name) > 0:
                    g.groupname = name[0].strip()
                else:
                    g.groupname = None

                if len(creator) > 0:
                    g.creatorprofileurl = creator[0].strip()
                else:
                    g.creatorprofileurl = None

                g.keyword = config.KEYWORD
                session.add(g)

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
        p = SpiderProfile()

        html = scrapy.Selector(text=str(item['body']))

        username = html.xpath(
            '//div[@class="viewJobInfo"]/span[@class="profileLabel" and @aria-label="User Name:"]/../text()').extract()
        peoplename = html.xpath('//span[@class="member_name"]/text()').extract()

        print(username)

        if len(username) > 0:
            p.username = username[1].replace('\\n', '').strip()
        else:
            p.username = None

        if len(peoplename) > 0:
            p.peoplename = peoplename[0].strip()
        else:
            p.peoplename = None

        p.url = str(item['url'])
        p.body = str(item['body'])
        p.createtime = datetime.datetime.now()

        if p.username and p.peoplename:
            session = sessionmaker(bind=self.engine)()
            session.add(p)
            session.commit()
            session.close()

        return item

    def __process_jam_profile_group_spider(self, item):
        if 'groups' in item.keys() and item['groups'] is not None:
            engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
            sql = "update jam_profile set groups = :groups where id = :id"
            para = {"groups": str(item["groups"]), "id": int(item["id"])}
            engine.execute(text(sql), para)
            # engine.execute(f'update jam_profile set groups="{pymysql.escape_string(str(item["groups"]))}" where id = {item["id"]}')
        else:
            print('no groups:', item['username'])

        return item

    def __process_jam_profile_follow_spider(self, item):
        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

        if 'followers' in item.keys():
            sql = "update jam_profile set followers=:followers where id = :id"
            para = {"followers": str(item['followers']), "id": int(item['id'])}
            engine.execute(text(sql), para)

        if 'following' in item.keys():
            sql = "update jam_profile set following=:following where id = :id"
            para = {"following": str(item['following']), "id": int(item['id'])}
            engine.execute(text(sql), para)

        return item

    def __process_portal_profile_spider(self, item):
        p = SpiderPortalProfile()

        p.username = str(item['username'])
        p.url = str(item['url'])
        p.body = str(item['body'])
        p.createtime = datetime.datetime.now()

        if p.username and p.body != '[]':
            session = sessionmaker(bind=self.engine)()
            session.add(p)
            session.commit()
            session.close()

        return item

    def __process_portal_profile_manager_spider(self, item):
        if str(item['body']) == '[]':
            return

        html = scrapy.Selector(text=str(item['body']))
        user_name = html.xpath('//div[@class="col-lg-2 col-md-4 col-sm-4 col-xs-12 customize uid"]'
                               '//div[@class="table-cell"]/span[@class="value"]/text()').extract()
        manager = html.xpath('//div[@class="col-lg-2 col-md-4 col-sm-4 col-xs-12 customize manager_link"]'
                             '//div[@class="table-cell"]/span[@class="value"]/a/text()').extract()
        manager_href = html.xpath('//div[@class="col-lg-2 col-md-4 col-sm-4 col-xs-12 customize manager_link"]'
                                  '//div[@class="table-cell"]/span[@class="value"]/a/@href').extract()
        assistant = html.xpath('//div[@class="col-lg-2 col-md-4 col-sm-4 col-xs-12 customize assistant_link"]'
                               '//div[@class="table-cell"]/span[@class="value"]/a/text()').extract()
        assistant_href = html.xpath('//div[@class="col-lg-2 col-md-4 col-sm-4 col-xs-12 customize assistant_link"]'
                                    '//div[@class="table-cell"]/span[@class="value"]/a/@href').extract()

        username = user_name[0].replace('\\n', '').strip()
        print(user_name, manager, manager_href, assistant, assistant_href)

        if username == item['url'].split('/')[-1]:
            m_val = [{"name": manager[0].replace('\\n', '').strip(),
                      "username": manager_href[0].split('/')[-1]}] if manager and manager_href else None
            a_val = [{"name": assistant[0].replace('\\n', '').strip(),
                      "username": assistant_href[0].split('/')[-1]}] if assistant and assistant_href else None

            if m_val is not None or a_val is not None:
                engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
                sql = '''update portal_profile set manager=:manager, assistant=:assistant where id=:id'''
                para = {'manager': str(m_val), 'assistant': str(a_val), 'id': int(item['id'])}
                engine.execute(text(sql), para)

        return item

    def __process_jam_comment_spider(self, item):
        if 'request_access' not in str(item['url']) and len(item['topics']) > 0:
            s = SpiderComment()
            s.url = str(item['url'])
            s.body = str(item['body'])
            s.topics = str(item['topics'])
            s.createtime = datetime.datetime.now()
            s.keyword = None

            session = sessionmaker(bind=self.engine)()
            session.add(s)
            session.commit()
            session.close()

        return item

    def __process_portal_successfactors_spider(self, item):
        print(str(item['id']))
        print(str(item['body']))

        if str(item['body']) == '':
            return

        # html = scrapy.Selector(text=str(item['body']))

