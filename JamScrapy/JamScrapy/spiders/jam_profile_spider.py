#!/usr/bin/env python
# -*- coding:utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest

from JamScrapy import config
from JamScrapy.items import JamScrapyProfileItem
from sqlalchemy import create_engine


class JamProfileSpider(scrapy.Spider):
    # 爬虫名称
    name = "JamProfileSpider"
    # 设置下载延时, 避免被BAN
    download_delay = 1
    # 允许域名
    allowed_domains = config.DOMAIN

    def start_requests(self):
        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        results = engine.execute("select distinct profileurl, displayname from jam_people_from_post "
                                 "where (username = '' or username is null) and displayname <> 'Alumni'")

        print(self.name, results.rowcount)

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

        for r in results:
            # yield scrapy.FormRequest(url, cookies=self.cookies, callback=self.parse)
            # 使用lua脚本，设置网关超时时间抓取网盘文件页面，设置meta传递id和抓取url
            # docker run -p 8050:8050 --name splash scrapinghub/splash --max-timeout 3600
            yield SplashRequest('https://' + config.DOMAIN + r.profileurl, callback=self.parse, endpoint='execute',
                                cache_args=['lua_source'],
                                args={'lua_source': script, 'timeout': 3600}, headers={'X-My-Header': 'value'},
                                meta={'displayname': r.displayname})

    def parse(self, response):
        item = JamScrapyProfileItem()

        # 当前URL
        item['peoplename'] = response.meta['displayname']
        item['url'] = response.url
        # item['body'] = response.body_as_unicode()
        # unicode_body = response.body_as_unicode()  # 返回的html unicode编码

        # sel : 页面源代码
        result = scrapy.Selector(response)

        item['body'] = result.xpath('//div[@id="jam-layout"]').extract()

        yield item
