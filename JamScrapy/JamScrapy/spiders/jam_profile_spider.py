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
    allowed_domains = [config.DOMAIN]
    # 开始URL
    start_urls = []

    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    results = engine.execute(
        'SELECT distinct displayname, profileurl FROM jam_people_from_post '
        'WHERE displayname <> \'Alumni\' AND keyword = \'blockchain\' ORDER BY displayname')

    # print(name, results.rowcount)

    def start_requests(self):
        # 自行初始化设置cookie
        script = """        
        function main(splash)         
          splash:init_cookies({
            {name="_ct_remember", value="1f4f40c78954618c", domain="jam4.sapjam.com"},
            {name="_ct_session", value="cldHTGNoVklLN0ZzZjBQMkROY3VhdUY3VUtkNHNsV3VPT3docUJ4Tm1VWDhIeDhaVkhLQ0tLUU9wdkNzYURpaFFUVDF0dW5XRm5oV1VFQnZpY25QK0pOT0o1QmxXNmRQOGZwNi9SV1F2NVBsR2hDdEpDY0VMOGdBUGNneHdhbFBqMEZIbWRGeW1lSGR2VXBPby9tWE5SZUR2SnZBRXVmRHN6bjlqRXh3YnpiRnRxUEZXYUNEMEljNkZRWDhHU3I4dkJGLzRCdXdCN2UydlhLT2RudEozVnp5UG93Ny9mQjVOYmZmZ3djZFJ4TEJaVEVqU1JnUHhOcUljY051dkxYbEF2WmxRUUdUd2dWWndQM1N4ZERFd00wVnJnWkNZTFF2TzM0bGVSWVQ5eHpTOVdtT2d0R3g1ejEwRjhCa3Y3TjdsZTc3alpPZ1RpU3ZtdGNZRUR4QVh5STZqV0ZFM2dFb1ladDdwVnI1SHc0bnVWZTRocWF1K2NWNkVQQWM2cEQ4WklhTy9VcnBubU52Q1M2cFoyNXdPbjNEUG40WHlMMzVoWmx5R2srVnFkS0dINkltREUyWlBWdWdLaExhbXNad3RSbTJESmJQQW95c2xoNUp4WEZpK3lFWE1Ja2JPYmgxcGpoNmFCclR5TXBpV1EvUWRGRUhONkNDajk1WmtHNzRTRjdMaCtsUW1hcmhFang1T1JJZ1dwUENMZTE3TStRTk9lUC9GM0FnUFBNVkFuTDBWamM2c1FYdXNaTVd4Z3FhOXZ2MGY3QXBicWNnZGNmQy9ISytiUFRESUZoaStVMHVRQlk0ZStxcDRNY09ESmMyNC9zYlAvV0FPQnpJSEIrbC0teU5tcUJXZWI0azE3SURoNTdqOWNHQT09--a728d29016462edf3ca08b9bf272c2a51c2dba3f", domain="jam4.sapjam.com"},
            {name="_ct_sso", value="jamatsap.com", domain="jam4.sapjam.com"},
            {name="_pk_id.2bcdec4d-0cbd-440f-9602-6bdee004700f.89e4", value="6e7a7619d8e75074.1523247974.0.1523247974..", domain="jam4.sapjam.com"},
            {name="_swa_id.2bcdec4d-0cbd-440f-9602-6bdee004700f.89e4", value="bc278ee358f38cc7.1523247974.1.1523248333.1523247974.", domain="jam4.sapjam.com"},          
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

        for r in self.results:
            # yield scrapy.FormRequest(url, cookies=self.cookies, callback=self.parse)
            # 使用lua脚本，设置网关超时时间抓取网盘文件页面，设置meta传递id和抓取url
            # docker run -p 8050:8050 --name splash scrapinghub/splash --max-timeout 3600
            yield SplashRequest('https://' + config.DOMAIN + r.profileurl, callback=self.parse, endpoint='execute',
                                cache_args=['lua_source'],
                                args={'lua_source': script, 'timeout': 3600}, headers={'X-My-Header': 'value'},
                                meta={'peoplename': r.displayname})

    def parse(self, response):
        item = JamScrapyProfileItem()

        # 当前URL
        item['peoplename'] = response.meta['peoplename']
        item['url'] = response.url
        # item['body'] = response.body_as_unicode()
        # unicode_body = response.body_as_unicode()  # 返回的html unicode编码

        # sel : 页面源代码
        result = scrapy.Selector(response)

        item['body'] = result.xpath('//div[@id="jam-layout"]').extract()

        yield item
