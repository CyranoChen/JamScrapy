#!/usr/bin/env python
# -*- coding:utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest

from sqlalchemy import create_engine

from JamScrapy import config
from JamScrapy.items import JamScrapySearchItem


class JamSearchCommentSpider(scrapy.Spider):
    # 爬虫名称
    name = "JamSearchCommentSpider"
    # 设置下载延时, 避免被BAN
    download_delay = 1
    # 允许域名
    allowed_domains = [config.DOMAIN]

    request_urls = []
    start_page = 1
    total_pages = config.SEARCH_SPIDER_PAGES

    def start_requests(self):
        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

        #https://jam4.sapjam.com/universal_search/search?page={0}&category=comments&query=
        url = '/universal_search/search?page={0}&category=comments'

        set_request_urls = set()
        for i in range(self.start_page, self.total_pages + 1, 1):
            set_request_urls.add('https://' + config.DOMAIN + url.format(i))

        sql = ""

        # 获取未处理的urls
        set_exist_urls_spider = set()

        results = engine.execute(f"select url from spider_jam_comment where topics <> '[]'").fetchall()

        for r in results:
            set_exist_urls_spider.add(r.url)

        self.request_urls = list(set_request_urls - set_exist_urls_spider)

        # 最终需要爬取的URL
        print('exist(spider) + require', len(set_exist_urls_spider), len(self.request_urls))
        print(self.name, len(self.request_urls))

        # 自行初始化设置cookie
        script = """        
        function main(splash)
          splash:init_cookies({
            {name="_ct_remember", value="#_ct_remember#", domain="jam4.sapjam.com"},
            {name="_ct_se", value="#_ct_se#", domain="jam4.sapjam.com"},
            {name="_ct_session", value="#_ct_session#", domain="jam4.sapjam.com"},
            {name="_ct_sso", value="#_ct_sso#", domain="jam4.sapjam.com"}    
          })
          
          assert(splash:go{
            splash.args.url,
            headers=splash.args.headers,
            http_method=splash.args.http_method,
            body=splash.args.body,
            })
          assert(splash:wait(5))
                   
          local entries = splash:history()
          local last_response = entries[#entries].response
          return {
            url = splash:url(),
            headers = last_response.headers,
            http_status = last_response.status,
            cookies = splash:get_cookies(),
            html = splash:html(),
          }
        end
        """

        script = script.replace('#_ct_remember#', config.JAM_COOKIE['_ct_remember'])
        script = script.replace('#_ct_se#', config.JAM_COOKIE['_ct_se'])
        script = script.replace('#_ct_session#', config.JAM_COOKIE['_ct_session'])
        script = script.replace('#_ct_sso#', config.JAM_COOKIE['_ct_sso'])

        for url in self.request_urls:
            # yield scrapy.FormRequest(url, cookies=self.cookies, callback=self.parse)
            yield SplashRequest(url, callback=self.parse, endpoint='execute', cache_args=['lua_source'],
                                args={'lua_source': script}, headers={'X-My-Header': 'value'})

    def parse(self, response):
        item = JamScrapySearchItem()

        # 当前URL
        item['url'] = response.url
        # item['body'] = response.body_as_unicode()
        # unicode_body = response.body_as_unicode()  # 返回的html unicode编码

        # sel : 页面源代码
        result = scrapy.Selector(response)

        # item['id'] = response.meta['id']
        item['topics'] = result.xpath('//li[@class="search_result"]/div[@class="title"]/span/a/@href').extract()
        item['body'] = 'ignore'
        # item['body'] = result.xpath('//div[@class="usr_results"]').extract()

        yield item
