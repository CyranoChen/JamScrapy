#!/usr/bin/env python
# -*- coding:utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest

from JamScrapy import config
from JamScrapy.items import JamScrapySearchItem
from sqlalchemy import create_engine


class JamGroupContentSpider(scrapy.Spider):
    # 爬虫名称
    name = "JamGroupContentSpider"
    # 设置下载延时, 避免被BAN
    download_delay = 1
    # 允许域名
    allowed_domains = [config.DOMAIN]

    request_urls = []

    def start_requests(self):
        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        results = engine.execute(f"select distinct groupurl from jam_group where keyword = '{config.KEYWORD}'")

        for r in results:
            self.request_urls.append(f"https://{config.DOMAIN}{r.groupurl}/content")

        print(self.name, len(self.request_urls))

        for url in self.request_urls:
            # yield scrapy.FormRequest(url, cookies=self.cookies, callback=self.parse)
            yield SplashRequest(url, callback=self.parse, endpoint='execute', cache_args=['lua_source'],
                                args={'lua_source': get_lua_script_with_cookie()},
                                headers={'X-My-Header': 'value'})

    def parse(self, response):
        item = JamScrapySearchItem()

        # 当前URL
        item['url'] = response.url
        # item['body'] = response.body_as_unicode()
        # unicode_body = response.body_as_unicode()  # 返回的html unicode编码

        # sel : 页面源代码
        result = scrapy.Selector(response)

        contents = result.xpath(
            '//table[@id="group_attachment_items"]//div[@class="content-item-name"]/a/@href').extract()

        if len(contents) > 0:
            item['topics'] = []
            for c in contents:
                if 'folder_id' not in str(c):
                    item['topics'].append(str(c))
                else:
                    yield SplashRequest(f"https://{config.DOMAIN}{str(c)}", callback=self.parse, endpoint='execute',
                                  cache_args=['lua_source'],
                                  args={'lua_source': get_lua_script_with_cookie()},
                                  headers={'X-My-Header': 'value'})

            # item['body'] = 'test'
            item['body'] = result.xpath('//div[@class="region-container"]').extract()

            yield item


def get_lua_script_with_cookie():
    # 自行初始化设置cookie
    script = """        
            function main(splash)
              splash:init_cookies({
                {name="_ct_remember", value="#_ct_remember#", domain="jam4.sapjam.com"},
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
    script = script.replace('#_ct_session#', config.JAM_COOKIE['_ct_session'])
    script = script.replace('#_ct_sso#', config.JAM_COOKIE['_ct_sso'])

    return script
