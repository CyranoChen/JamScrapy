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

    # print('results', results.rowcount)

    for r in results:
        request_urls.extend(ast.literal_eval(r.topics))

    # 全部URL
    # print(len(request_urls))

    set_request_urls = set()
    for r in request_urls:
        set_request_urls.add(r)

    # 全部不重复的URL set
    # print(len(set_request_urls))

    set_exist_urls = set()
    results = engine.execute(f"select baseurl from spider_jam_post where keyword = '{config.KEYWORD}'")

    for r in results:
        set_exist_urls.add(r.baseurl)

    # 全部已存在的URL set
    # print(len(set_exist_urls))

    request_urls = list(set_request_urls - set_exist_urls)

    # 最终需要爬取的URL
    # print(len(request_urls))

    def start_requests(self):
        # 自行初始化设置cookie
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
