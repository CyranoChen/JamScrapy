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
    #start_urls = engine.execute('SELECT distinct username FROM jam_profile')
    results = engine.execute('select distinct username from jam_profile where username not in (select username from spider_portal_profile)')

    print(name, results.rowcount)

    def start_requests(self):
        # 自行初始化设置cookie
        script = """        
        function main(splash)         
          splash:init_cookies({
            {name="BIGipServer~sap_it_corp_webapps-people_prod~lb-4c7322be4-e721", value="rd5o00000000000000000000ffff0a61073bo4000", domain="people.wdf.sap.corp"},
            {name="_expertondemand_session", value="BAh7CkkiD3Nlc3Npb25faWQGOgZFVEkiJTQwMWE3Njc2YjJiNzljMGMyMGVmNjBiZjk4YTY1N2E0BjsAVEkiCHVpZAY7AEZJIgxJMzQ1Nzk1BjsAVEkiDnJldHVybl90bwY7AEYiFi9wcm9maWxlcy9pMzQ1Nzk1SSIYYXZhaWxhYmlsaXR5X2Jhc2tldAY7AEZ7BjoJdWlkc1sASSIQX2NzcmZfdG9rZW4GOwBGSSIxYlUrNFFtWHArTEdsYjRGclNrRkZVajJFOWxObXJKcTJiVXppRnc3bTAxUT0GOwBG--fc2b73abd55d67b4181ad9faa9a9511bbcfed11a", domain="people.wdf.sap.corp"},  
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

        for item in self.results:
            # yield scrapy.FormRequest(url, cookies=self.cookies, callback=self.parse)
            # 使用lua脚本，设置网关超时时间抓取网盘文件页面，设置meta传递id和抓取url
            # docker run -p 8050:8050 --name splash scrapinghub/splash --max-timeout 3600
            yield SplashRequest('https://people.wdf.sap.corp/profiles/' + item.username.strip(), callback=self.parse, endpoint='execute',
                                cache_args=['lua_source'],
                                args={'lua_source': script, 'timeout': 3600}, headers={'X-My-Header': 'value'},
                                meta={'username': item.username})

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
