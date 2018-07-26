#!/usr/bin/env python
# -*- coding:utf-8 -*-
import scrapy
import json
from scrapy_splash import SplashRequest

from JamScrapy import config
from JamScrapy.items import JamScrapyProfileGroupItem
from sqlalchemy import create_engine


class JamProfileGroupSpider(scrapy.Spider):
    # 爬虫名称
    name = "JamProfileGroupSpider"
    # 设置下载延时, 避免被BAN
    download_delay = 1
    # 允许域名
    allowed_domains = [config.DOMAIN]
    # 开始URL
    start_urls = []

    def start_requests(self):
        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        results = engine.execute('SELECT * FROM jam_profile where (groups is null or groups = "") order by id')

        for item in results:
            uid = item.profileurl.split("/")[-1]
            self.start_urls.append({'id': item.id, 'username': item.username, 'url': '/groups/view/' + uid})

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

        # print(script)

        for item in self.start_urls:
            # yield scrapy.FormRequest(url, cookies=self.cookies, callback=self.parse)
            # 使用lua脚本，设置网关超时时间抓取网盘文件页面，设置meta传递id和抓取url
            # docker run -p 8050:8050 --name splash scrapinghub/splash --max-timeout 3600
            yield SplashRequest('https://' + config.DOMAIN + item['url'], callback=self.parse, endpoint='execute',
                                cache_args=['lua_source'],
                                args={'lua_source': script, 'timeout': 3600}, headers={'X-My-Header': 'value'},
                                meta={'id': item['id'], 'username': item['username'], 'url': item['url']})

    def parse(self, response):
        item = JamScrapyProfileGroupItem()

        # 当前URL
        item['id'] = response.meta['id']
        item['username'] = response.meta['username']
        item['url'] = response.url
        # item['body'] = response.body_as_unicode()
        # unicode_body = response.body_as_unicode()  # 返回的html unicode编码

        # sel : 页面源代码
        result = scrapy.Selector(response)

        groups = result.xpath('//div[@id="groupProjectList"]//div[@class="group_name public"]/a/text()').extract()
        group_overviews = result.xpath(
            '//div[@id="groupProjectList"]//div[@class="group_name public"]/a/@href').extract()

        if groups:
            json_groups = []
            for i in range(len(groups)):
                json_groups.append({'name': groups[i], 'url': group_overviews[i]})
                item['groups'] = json.dumps(json_groups)

        yield item
