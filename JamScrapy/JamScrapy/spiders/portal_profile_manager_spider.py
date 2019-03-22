#!/usr/bin/env python
# -*- coding:utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest

from JamScrapy import config
from JamScrapy.items import PortalScrapyProfileItem
from sqlalchemy import create_engine


class PortalProfileManagerSpider(scrapy.Spider):
    # 爬虫名称
    name = "PortalProfileManagerSpider"
    # 设置下载延时, 避免被BAN
    download_delay = 5
    # 允许域名
    allowed_domains = ['portal.wdf.sap.corp']

    request_urls = []

    def start_requests(self):
        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        results = engine.execute('select id, profileurl from portal_profile order by id').fetchall()

        self.request_urls = [(x.id, x.profileurl) for x in results]

        print(self.name, len(self.request_urls))

        # 自行初始化设置cookie
        script = """        
        function main(splash)         
          splash:init_cookies({
            {name="BIGipServer~sap_it_corp_webapps-people_prod~lb-4c7322be4-e721", value="rd5o00000000000000000000ffff0a610634o4000", domain="people.wdf.sap.corp"},
            {name="_expertondemand_session", value="BAh7CkkiD3Nlc3Npb25faWQGOgZFVEkiJTNiZjdjMjRjMDMyMWQ0NzY3YjhhODkzYTFiOGE1NGRlBjsAVEkiCHVpZAY7AEZJIgxJMzQ1Nzk1BjsAVEkiDnJldHVybl90bwY7AEYiFy9wcm9maWxlcy9DMTAxNjY4OUkiGGF2YWlsYWJpbGl0eV9iYXNrZXQGOwBGewY6CXVpZHNbAEkiEF9jc3JmX3Rva2VuBjsARkkiMXdCRzB1aFpocnFsYTFpS1pHeFFaZVRWUlU4TjVyVUd0MFBXd3RwWFdzbDQ9BjsARg%3D%3D--1b42f9d945e498f9eb5b749afcdb62e861a24048", domain="people.wdf.sap.corp"},  
            {name="_pk_id.b2fbf9a2-64b4-46d6-b19d-8699f0a3d43e.2ff0", value="64560c865b78216c.1548744190.0.1548744481..", domain="people.wdf.sap.corp"},
            {name="_swa_v_id.b2fbf9a2-64b4-46d6-b19d-8699f0a3d43e.2ff0", value="e5908e0426c7977a.1548744190.1.1548744481.1548744190.", domain="people.wdf.sap.corp"},
            {name="_swa_v_ref.b2fbf9a2-64b4-46d6-b19d-8699f0a3d43e.2ff0", value="%5B%22%22%2C%22%22%2C1548744190%2C%22https%3A%2F%2Fsearch.int.sap%2F%22%5D", domain="people.wdf.sap.corp"},
            {name="_swa_v_ses.b2fbf9a2-64b4-46d6-b19d-8699f0a3d43e.2ff0", value="*", domain="people.wdf.sap.corp"},
            {name="shpuvid", value="CmEGNFxP9foDjw6TBn/JAg==", domain=".sap.corp"}     
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

        for id, url in self.request_urls:
            # yield scrapy.FormRequest(url, cookies=self.cookies, callback=self.parse)
            # 使用lua脚本，设置网关超时时间抓取网盘文件页面，设置meta传递id和抓取url
            # docker run -p 8050:8050 --name splash scrapinghub/splash --max-timeout 3600
            yield SplashRequest(url, callback=self.parse,
                                endpoint='execute',
                                cache_args=['lua_source'],
                                args={'lua_source': script, 'timeout': 3600}, headers={'X-My-Header': 'value'},
                                meta={'id': id})

    def parse(self, response):
        item = PortalScrapyProfileItem()

        # 当前URL
        item['id'] = response.meta['id']
        item['url'] = response.url
        # item['body'] = response.body_as_unicode()
        # unicode_body = response.body_as_unicode()  # 返回的html unicode编码

        # sel : 页面源代码
        result = scrapy.Selector(response)

        item['body'] = result.xpath('//div[@class="main-profile-info"]').extract()

        yield item
