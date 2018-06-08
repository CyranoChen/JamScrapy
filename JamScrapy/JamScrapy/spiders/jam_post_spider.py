#!/usr/bin/env python
# -*- coding:utf-8 -*-
import scrapy
import ast
from scrapy_splash import SplashRequest

from sqlalchemy import create_engine

from JamScrapy import config
from JamScrapy.items import JamScrapyPostItem


class JamPostSpider(scrapy.Spider):
    # 爬虫名称
    name = "JamPostSpider"
    # 设置下载延时, 避免被BAN
    download_delay = 1
    # 允许域名
    allowed_domains = [config.DOMAIN]
    # 开始URL
    request_urls = []

    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    results = engine.execute(f"select * from spider_jam_search where body <> '[]' and keyword = '{config.KEYWORD}'")

    print(name, results.rowcount)

    for r in results:
        request_urls.extend(ast.literal_eval(r.topics))

    def start_requests(self):
        # 自行初始化设置cookie
        script = """        
        function main(splash)         
          splash:init_cookies({
            {name="_ct_remember", value="136b5c2b205f2b86", domain="jam4.sapjam.com"},
            {name="_ct_session", value="QzdNTitBa2p6c2NIOHFtM2lyM3JnWkVvUFpEMHNMM2laYUc1RXdJWFVHZ1VxVER0bUlmMlMzT1lDdjZsYTc5Nkp2WDhsdTRUNmp3V1l2ekZJcHIzYzlhbktDM1hQdzhPQVFUcVNPQVdEWlo3ekl1L1lpUVh3d3VrcWhJbWlIbTBtUEUyclBFczB1cXpuMzdmbFpnVjJNNUcycXhJa3ovSHFvNHZRamJCWlRsRkJTYlRhdnNhN2RlbFFxKzk3WDNqNmg3R0F0U3NMeUVleW1VdFlOd0loZUFpaHQ3bFlVUVdQQis5OTF4RGV0R25aUVhPV3pWT1R3VDhGY0RRK0VyUHNlUE9LYXMwcytBRVVvVm5DSFl1NHpSV203bXA0UGhMUDl0NnhFRXNaVndYbUNXdzBIeDVSeXluYStFekNaV3oyOFBDTmpzWCtodWwwRUpxcG9FQnh1SDJSWmVrQnRjN2ZJK3FKd1plU0xUNTcyVjJjaFhFS3BWNWQ1ajROT1FLOGsxWGFWUkRZb2d6NUxpZkpnTmhvVzBOeG94bWtrcHdVdHlwNE44dnJZTUJJQytxODVrQWdhMXVHeHhFa1lYOFF2ZE1Md3RMY1p6RWthTlB5TUY5YldrZVh3aWRlZGJleVd1YmtoU0VyRVpUTDZWV05jdzNpZ2d0RS9lMlErMWJtN1NPc0J1MUZ3L2hLdGdEajZkdEZpL3NYRTdzV0E3cCtSdUNTeTJLWTFQazZGVURmNkIwUU53ZE5KT2VycnZDbEZ4MGRyUDlEaHN5a3pxUDJXbG9peS9tSkU2NC9IQ1llOUhoNlhXNjNyQlB2TnZONVpaUUVadHpOWnh6NXRWbC0td0hoZzBIWHpCbzU4Q2Q4WkpwM1BCUT09--1cab28eebbf0c902ac9c84244eee661e7e027c2d", domain="jam4.sapjam.com"},
            {name="_ct_sso", value="jamatsap.com", domain="jam4.sapjam.com"}   
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

        for url in self.request_urls:
            # yield scrapy.FormRequest(url, cookies=self.cookies, callback=self.parse)
            # 使用lua脚本，设置网关超时时间抓取网盘文件页面，设置meta传递id和抓取url
            # docker run -p 8050:8050 --name splash scrapinghub/splash --max-timeout 3600
            yield SplashRequest(url, callback=self.parse, endpoint='execute', cache_args=['lua_source'],
                                args={'lua_source': script, 'timeout': 3600}, headers={'X-My-Header': 'value'},
                                meta={'baseurl': url})

    def parse(self, response):
        item = JamScrapyPostItem()

        # 当前URL
        #item['id'] = response.meta['id']
        item['baseurl'] = response.meta['baseurl']
        item['url'] = response.url
        # item['body'] = response.body_as_unicode()
        # unicode_body = response.body_as_unicode()  # 返回的html unicode编码

        # sel : 页面源代码
        result = scrapy.Selector(response)

        item['body'] = result.xpath('//div[@id="jam-layout"]').extract()

        yield item
