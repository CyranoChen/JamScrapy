#!/usr/bin/env python
# -*- coding:utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from JamScrapy import config
from JamScrapy.items import JamScrapyGroupItem


class JamGroupSpider(scrapy.Spider):
    # 爬虫名称
    name = "JamGroupSpider"
    # 设置下载延时, 避免被BAN
    download_delay = 1
    # 允许域名
    allowed_domains = [config.DOMAIN]

    request_urls = []
    start_page = 1
    total_pages = config.GROUP_SPIDER_PAGES

    def start_requests(self):
        url = '/universal_search/search?category=groups&page={1}&query="{0}"'

        for i in range(self.start_page, self.total_pages + 1, 1):
            self.request_urls.append('https://' + config.DOMAIN + url.format(config.KEYWORD, i))

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
            yield SplashRequest(url, callback=self.parse, endpoint='execute', cache_args=['lua_source'],
                                args={'lua_source': script}, headers={'X-My-Header': 'value'})

    def parse(self, response):
        item = JamScrapyGroupItem()

        # 当前URL
        item['url'] = response.url
        # item['body'] = response.body_as_unicode()
        # unicode_body = response.body_as_unicode()  # 返回的html unicode编码

        # sel : 页面源代码
        result = scrapy.Selector(response)

        # item['id'] = response.meta['id']
        item['groups'] = result.xpath('//li[@class="search_result"]').extract()
        # item['body'] = 'test'
        # item['body'] = result.xpath('//div[@class="usr_results"]').extract()

        yield item
