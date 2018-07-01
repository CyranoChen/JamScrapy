#!/usr/bin/env python
# -*- coding:utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from sqlalchemy import create_engine
from JamScrapy import config
from JamScrapy.items import JamScrapySearchItem


class JamSearchFetchSpider(scrapy.Spider):
    # 爬虫名称
    name = "JamSearchFetchSpider"
    # 设置下载延时, 避免被BAN
    download_delay = 1
    # 允许域名
    allowed_domains = [config.DOMAIN]

    request_urls = []

    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    results = engine.execute(f"select * from spider_jam_search where body = '[]' and keyword = '{config.KEYWORD}'")

    # print(name, results.rowcount)

    def start_requests(self):
        script = """        
        function main(splash)
          splash:init_cookies({
            {name="_ct_remember", value="1ac7b1a816057bee", domain="jam4.sapjam.com"},
            {name="_ct_session", value="Yk82eVZ5enlIcUp3c3Q2VDNhandnL1I0dFlQOURtcmVjZWdZdWxrMzgzekFlQ3MyU29oVTZpU2RhWFN2ZmRCTjd1VHlkQ1A4OFVtVE9hai8xemNWOWIvU3BNbERMbDg2QkMrRzM1bkhqLzRZV0Z5NGNmbFp0SGVYMEl2NGE0Mk1yOFMzeGNXZmxWV2k2ZHh1bUNIRldYcnRCVXBUb1hpb3BNYzRxdzc2RzgwNTNZZkR6MGVrSXhESlJaRXgvc010bG04MWl1dWk0d05zWGt2QTZuNkxjVWtMalF4SDBQdmtyTWcrMG40M0VpVEc5b3MwcXZNUVJlZ0JjL0ZBbzFwWTkyRUt1L2NqUHJKOEZzTXpUSmtDbG14UFIzV3RRZk15RThmaGdUeDNXUXFkNmdySEk4cXJxRDVjdHJ5aFlnZnB1dTE4bi9FZ2tSUjVDc0dPaE5zdFc0Q2NEeHFFMk1nR3o1UW1ReVVwdlNiOThiY1ErZWZ1Z2NzMHJRcWxoSFEwWElnSTJiamVGQ2pZem92VHU3UmtZQjZ6OHQ1NmFwWnBSMnFBWEhvdXo0SkZQbXJhdkNxS2N3M2kzUXFEVGNsa3JJVnNRRDhnd2NCc3g4TXdKc0VEclZNN3NMMHRiL0Z2TGozaHBWVk5TYjlLS0sxdWdxY1FIWjJZcTZJVUlITXJVNFA3OFVub3FKUkVhczlFaHR5SmxJVEpKVjZkRi9oTGViei8zdVFEVjRnSHEwbm5NR1Z5eWxvYVlHc2h4cWY5b29ZdEN2NHpZVmdQQzhxd2szUFIyWVdsT0NnQm9halhIME5PV1F2ZGtGNVhGbU1PYUhBZ2UvZXU0UU5DeXF4Uy0talJIZDAvTlpBMUhvQjRsUlBGaVMzdz09--ac23fc93f1d0baf132e68dc4c5844767a02f6e5b", domain="jam4.sapjam.com"},
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

        for r in self.results:
            # yield scrapy.FormRequest(url, cookies=self.cookies, callback=self.parse)
            yield SplashRequest(r.url, callback=self.parse, endpoint='execute', cache_args=['lua_source'],
                                args={'lua_source': script}, headers={'X-My-Header': 'value'},
                                meta={'id': r.id})

    def parse(self, response):
        item = JamScrapySearchItem()

        # 当前URL
        item['url'] = response.url
        # item['body'] = response.body_as_unicode()
        # unicode_body = response.body_as_unicode()  # 返回的html unicode编码

        # sel : 页面源代码
        result = scrapy.Selector(response)

        item['id'] = response.meta['id']
        item['topics'] = result.xpath('//li[@class="search_result"]/div[@class="title"]/span/a/@href').extract()
        item['body'] = result.xpath('//div[@class="usr_results"]').extract()

        yield item
