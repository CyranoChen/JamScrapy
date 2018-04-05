#!/usr/bin/env python
# -*- coding:utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest

from JamScrapy import config
from JamScrapy.items import PortalScrapyProfileItem
from sqlalchemy import create_engine


class PortalProfileSpider(scrapy.Spider):
    # 爬虫名称
    name = "PortalProfileSpider"
    # 设置下载延时, 避免被BAN
    download_delay = 1
    # 允许域名
    allowed_domains = ['people.wdf.sap.corp']
    # 开始URL
    start_urls = []

    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    start_urls = engine.execute('SELECT distinct username FROM jam_profile')

    def start_requests(self):
        # 自行初始化设置cookie
        script = """        
        function main(splash)         
          splash:init_cookies({
            {name="BIGipServer~sap_it_corp_webapps-people_prod~lb-4c7322be4-e721", value="rd5o00000000000000000000ffff0a610634o4000", domain="people.wdf.sap.corp"},
            {name="_expertondemand_session", value="BAh7CkkiD3Nlc3Npb25faWQGOgZFVEkiJTEzYjNmYjk1MzQ4ODE1YmQ1MDMwMjc3M2MzNzcyZWJkBjsAVEkiCHVpZAY7AEZJIgxJMzQ1Nzk1BjsAVEkiDnJldHVybl90bwY7AEYiFi9wcm9maWxlcy9JMzQ1Nzk1SSIYYXZhaWxhYmlsaXR5X2Jhc2tldAY7AEZ7BjoJdWlkc1sASSIQX2NzcmZfdG9rZW4GOwBGSSIxRHI4ZWRhZU9Oc2xDTjFOVVpaUXI4OXNXSC9NSnJ0NS8wa0tOcDN6NHlZUT0GOwBG--b1487f81e8b692c5a5aa6d206aabe7e4d08e9b8f", domain="people.wdf.sap.corp"},
            {name="_pk_id.b2fbf9a2-64b4-46d6-b19d-8699f0a3d43e.2ff0", value="079503e80c5ee7da.1520840692.0.1522642984..", domain="people.wdf.sap.corp"},
            {name="_swa_id.b2fbf9a2-64b4-46d6-b19d-8699f0a3d43e.2ff0", value="8588e3f8f9e877eb.1520840692.3.1522644067.1522210200.", domain="people.wdf.sap.corp"},
            {name="_swa_ref.b2fbf9a2-64b4-46d6-b19d-8699f0a3d43e.2ff0", value="%5B%22%22%2C%22%22%2C1522642972%2C%22https%3A%2F%2Fsearch.int.sap%2F%22%5D", domain="people.wdf.sap.corp"},          
            {name="_swa_ses.b2fbf9a2-64b4-46d6-b19d-8699f0a3d43e.2ff0", value="*", domain="people.wdf.sap.corp"},    
            {name="shpuvid", value="CmEHO1qmL+9wEAlfBsKNAg==", domain=".sap.corp"}     
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

        for item in self.start_urls:
            # yield scrapy.FormRequest(url, cookies=self.cookies, callback=self.parse)
            # 使用lua脚本，设置网关超时时间抓取网盘文件页面，设置meta传递id和抓取url
            # docker run -p 8050:8050 --name splash scrapinghub/splash --max-timeout 3600
            yield SplashRequest('https://people.wdf.sap.corp/profiles/' + item.username.strip(), callback=self.parse, endpoint='execute',
                                cache_args=['lua_source'],
                                args={'lua_source': script, 'timeout': 3600}, headers={'X-My-Header': 'value'},
                                meta={'username': item.username })

    def parse(self, response):
        item = PortalScrapyProfileItem()

        # 当前URL
        item['username'] = response.meta['username']
        item['url'] = response.url
        # item['body'] = response.body_as_unicode()
        # unicode_body = response.body_as_unicode()  # 返回的html unicode编码

        # sel : 页面源代码
        result = scrapy.Selector(response)

        item['body'] = result.xpath('//div[@class="main-profile-info"]').extract()

        yield item
