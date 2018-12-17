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
    download_delay = 5
    # 允许域名
    allowed_domains = ['people.wdf.sap.corp']

    request_urls = []

    def start_requests(self):
        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        results = engine.execute('select distinct username from jam_profile where (username is not null or username <> "") and '
                                 'username not in (select username from portal_profile)')

        print(self.name, results.rowcount)

        set_username_urls = set()
        for r in results:
            set_username_urls.add(r.username)

        set_exist_username_spider = set()
        results = engine.execute(f"select distinct username from spider_portal_profile")

        for r in results:
            set_exist_username_spider.add(r.username)

        self.request_urls = list(set_username_urls - set_exist_username_spider)

        print('exist(spider) + require', len(set_exist_username_spider), len(self.request_urls))

        print(self.name, len(self.request_urls))

        # 自行初始化设置cookie
        script = """        
        function main(splash)         
          splash:init_cookies({
            {name="BIGipServer~sap_it_corp_webapps-people_prod~lb-4c7322be4-e721", value="rd5o00000000000000000000ffff0a610634o4000", domain="people.wdf.sap.corp"},
            {name="_expertondemand_session", value="BAh7DkkiD3Nlc3Npb25faWQGOgZFVEkiJTQyNGJjODlhNzY2MDQ2ZGRlZGJlYjM2OGM1YmNkZGRkBjsAVEkiCHVpZAY7AEZJIgxJMzQ1Nzk1BjsAVEkiDnJldHVybl90bwY7AEYiFi9wcm9maWxlcy9JMzQ1Nzk1SSIYYXZhaWxhYmlsaXR5X2Jhc2tldAY7AEZ7BjoJdWlkc1sASSIQX2NzcmZfdG9rZW4GOwBGSSIxeXV4Mm5TZGpnN05rSDlDMytTS0NaMktUT2c5blREVnRrWStVWDhWOWlmcz0GOwBGSSILcnRva2VuBjsARkkiLTc3LS1mOGU4OTg2YS0zZTljLTRlOWQtOWFjNS0xMWQ0ZTQ4ZWI3ODAGOwBUSSIMcnNlY3JldAY7AEZJIikxMDMyYTMyNi05ZGU3LTRlZmItOTYzNy1kYTAxMDg1NTFiZGQGOwBUSSILYXRva2VuBjsARkkiKWQyMjljNDNkLTY1ZGItNGJmYi1hMzA2LWQ2Y2QyY2FjNTY0NAY7AFRJIgxhc2VjcmV0BjsARkkiKTRmZDliY2MwLTJkYmUtNGJkNy1hMDg1LWRiYWUyYjk3ZmM4ZgY7AFQ%3D--6a6a39335da7fa958b44fe0d8466021a7b02b6cc", domain="people.wdf.sap.corp"},  
            {name="_pk_id.b2fbf9a2-64b4-46d6-b19d-8699f0a3d43e.2ff0", value="03931306e91b305c.1542597044.0.1543977112..", domain="people.wdf.sap.corp"},
            {name="_swa_v_id.b2fbf9a2-64b4-46d6-b19d-8699f0a3d43e.2ff0", value="635b071493dfd52c.1542597044.10.1543977112.1543552484.", domain="people.wdf.sap.corp"},
            {name="_swa_v_ref.b2fbf9a2-64b4-46d6-b19d-8699f0a3d43e.2ff0", value="%5B%22%22%2C%22%22%2C1543977070%2C%22https%3A%2F%2Fwww.linkedin.com%2Fuas%2Foauth%2Fauthorize%2Fsubmit%22%5D", domain="people.wdf.sap.corp"},
            {name="_swa_v_ses.b2fbf9a2-64b4-46d6-b19d-8699f0a3d43e.2ff0", value="*", domain="people.wdf.sap.corp"},
            {name="shpuvid", value="CmEHO1s55ySNCQm4BNojAg==", domain=".sap.corp"}     
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

        for username in self.request_urls:
            # yield scrapy.FormRequest(url, cookies=self.cookies, callback=self.parse)
            # 使用lua脚本，设置网关超时时间抓取网盘文件页面，设置meta传递id和抓取url
            # docker run -p 8050:8050 --name splash scrapinghub/splash --max-timeout 3600
            yield SplashRequest('https://people.wdf.sap.corp/profiles/' + username.strip(), callback=self.parse, endpoint='execute',
                                cache_args=['lua_source'],
                                args={'lua_source': script, 'timeout': 3600}, headers={'X-My-Header': 'value'},
                                meta={'username': username.strip()})

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
