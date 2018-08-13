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

    request_urls = []

    def start_requests(self):
        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        results = engine.execute("select distinct profileurl from jam_people_from_post "
                                 "where (username = '' or username is null) and displayname <> 'Alumni'")

        set_profile_urls = set()
        for r in results:
            set_profile_urls.add(r.profileurl.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', ''))

        print('distinct post (processed) url', len(set_profile_urls), '/', results.rowcount)

        # 获取未处理的urls
        set_exist_profile_urls_spider = set()
        results = engine.execute(f"select distinct url from spider_jam_profile")

        for r in results:
            set_exist_profile_urls_spider.add(r.url.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', ''))

        # 获取已处理的profile urls
        set_exist_profile_urls = set()
        results = engine.execute(f"select distinct profileurl from jam_profile")

        for r in results:
            set_exist_profile_urls.add(r.profileurl.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', ''))

        self.request_urls = list(set_profile_urls - set_exist_profile_urls_spider - set_exist_profile_urls)

        # 最终需要爬取的URL
        print('exist(spider) + exist(processed) + require', len(set_exist_profile_urls_spider),
              len(set_exist_profile_urls), len(self.request_urls))

        print(self.name, len(self.request_urls))

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

        for url in self.request_urls:
            # yield scrapy.FormRequest(url, cookies=self.cookies, callback=self.parse)
            # 使用lua脚本，设置网关超时时间抓取网盘文件页面，设置meta传递id和抓取url
            # docker run -p 8050:8050 --name splash scrapinghub/splash --max-timeout 3600
            yield SplashRequest('https://' + config.DOMAIN + url, callback=self.parse, endpoint='execute',
                                cache_args=['lua_source'],
                                args={'lua_source': script, 'timeout': 3600}, headers={'X-My-Header': 'value'})

    def parse(self, response):
        item = JamScrapyProfileItem()

        # 当前URL
        item['url'] = response.url
        # item['body'] = response.body_as_unicode()
        # unicode_body = response.body_as_unicode()  # 返回的html unicode编码

        # sel : 页面源代码
        result = scrapy.Selector(response)

        item['body'] = result.xpath('//div[@id="jam-layout"]').extract()

        yield item