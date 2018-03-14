#!/usr/bin/env python
# -*- coding:utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest

from JamScrapy import config
from JamScrapy.items import JamScrapyListItem


class JamSearchSpider(scrapy.Spider):
    # 爬虫名称
    name = "JamSearchSpider"
    # 设置下载延时, 避免被BAN
    download_delay = 2
    # 允许域名
    allowed_domains = [config.DOMAIN]
    # 开始URL
    start_urls = []
    for i in [1]:
    #for i in range(1, 141, 1):
        start_urls.append('https://' + config.DOMAIN + config.START_SEARCH_URL.format(config.KEYWORD, i))

    # 爬取规则,不带callback表示向该类url递归爬取
    # rules = (
    #     Rule(LinkExtractor(allow=('page/[0-9]+',))),
    #     Rule(LinkExtractor(allow=('recipe-[0-9]+',)), callback='parse_content'),
    # )

    def start_requests(self):
        script = """        
        function main(splash)
          splash:init_cookies({
            {name="_ct_remember", value="06b2bff297aa3bc7", domain="jam4.sapjam.com"},
            {name="_ct_session", value="VGRxczJiRWJSM1gzNEFuTlZHSzkxVlJyODhaaVZUNmY5RFd0RktiNEZRcHI1YkRxKzc3ZTlkTXRqR1pQbWhUdVVKT3B0QmdUSWdSdlRrMDlnaTBFd1FlY2xLZi9MOFY1YjhDVUFUbWQ5TWVvUm80UmE5byt0dExCU3poVmk3NDBBR1p4ajE0OUFidlpNTFd3cUZQditwYyt2WmpBMndDVWlyZUFtZW1PSTg1cDBLZTczUlpRZ0hScHRxUHAxb2d4dVRKalpVRTNoWVEyN0xUeEVpVlNRSmQrK1RyalN4WjZIOWJ6NDRrRXhPUXZ3VndycFV5djE5R01YdThyay84RSsvdndhdTB0Qlg1RklPejR1WUJuYytmM0gyWUdSZUxkbE1acUs3UndHdWxPRmJGVVg1dmdybzBjVTRyYTc2YmNQek1pSDZDelpKQTZ1TEQ4K0lhTVZHbWN4aEdEZkZMa1R0VHVJc3lmcDhtcC9hdWp3Wk14cGl0VXBCWk12c2pRbDF3RDNKR1NhdDhCRVg5MG03YnRZSkZINVQ4SXpqeFNuL2NEOEh5M1lHczAxNUEvWGhjbDM5UzR3ckkwWWNKRHdxdVN4cHlQbGdTZFZaOFlyU0VBT2VoRlJRbWhCazNYNGJ2WWM3THB6bDVUaVhrb29LM3dsNERFRGdZYnhyY2NJeHJ0RW5zOGl0RlhTWGdwR3ByNWRXT2h3TVdVdEljQnFVZk5OU2Q2SkgrZnExY2hxb0piNVczUEpLcmlZdFZqNHhIZkZLcDRRYVdCakN5cmtabzdaZ3o4cjRwbHJZNW1VMzRmN29hVUVSR29qQTFybG4xV1lvbmVYZ0IwUmpYdS0telRQTlFRNnF6VnVLUGNSQVJhK2V0UT09--9fa36dafa14437eee85749cbbb8028ea050cb9a4", domain="jam4.sapjam.com"},
            {name="_ct_sso", value="06b2bff297aa3bc7", domain="jam4.sapjam.com"},
            {name="_pk_id.2bcdec4d-0cbd-440f-9602-6bdee004700f.89e4", value="9aa43982ac568099.1520411233.0.1520411233..", domain="jam4.sapjam.com"},
            {name="_swa_id.2bcdec4d-0cbd-440f-9602-6bdee004700f.89e4", value="41d407f316823a9b.1520411233.1.1520411234.1520411233.", domain="jam4.sapjam.com"},          
            {name="_swa_ses.2bcdec4d-0cbd-440f-9602-6bdee004700f.89e4", value="*", domain="jam4.sapjam.com"}     
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

        for url in self.start_urls:
            # yield scrapy.FormRequest(url, cookies=self.cookies, callback=self.parse)
            yield SplashRequest(url, callback=self.parse, endpoint='execute', cache_args=['lua_source'], args={'lua_source': script}, headers={'X-My-Header': 'value'})

    def parse(self, response):
        item = JamScrapyListItem()

        # 当前URL
        item['url'] = response.url
        # item['body'] = response.body_as_unicode()
        # unicode_body = response.body_as_unicode()  # 返回的html unicode编码

        # sel : 页面源代码
        result = scrapy.Selector(response)

        item['topics'] = result.xpath('//li[@class="search_result"]/div[@class="title"]/span/a/@href').extract()
        #item['body'] = 'test'
        item['body'] = result.xpath('//div[@class="usr_results"]').extract()

        yield item
