#!/usr/bin/env python
# -*- coding:utf-8 -*-
import scrapy
import json
from scrapy_splash import SplashRequest

from JamScrapy import config
from JamScrapy.items import JamScrapyProfileFollowItem
from sqlalchemy import create_engine


class JamProfileFollowSpider(scrapy.Spider):
    # 爬虫名称
    name = "JamProfileFollowSpider"
    # 设置下载延时, 避免被BAN
    download_delay = 1
    # 允许域名
    allowed_domains = [config.DOMAIN]
    # 开始URL
    start_urls = []

    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    results = engine.execute('SELECT * FROM jam_profile order by id')

    # print(name, results.rowcount)

    for item in results:
        uid = item.profileurl.split("/")[-1]
        start_urls.append({'id': item.id, 'display_name': item.displayname, 'url': '/profile/social_graph/' + uid})

    def start_requests(self):
        # 自行初始化设置cookie
        script = """        
        function main(splash)         
          splash:init_cookies({
            {name="_ct_remember", value="#_ct_remember#", domain="jam4.sapjam.com"},
            {name="_ct_session", value="#_ct_session#", domain="jam4.sapjam.com"},
            {name="_ct_sso", value="#_ct_sso#", domain="jam4.sapjam.com"},
            {name="_pk_id.2bcdec4d-0cbd-440f-9602-6bdee004700f.89e4", value="#_pk_id#", domain="jam4.sapjam.com"},
            {name="_swa_id.2bcdec4d-0cbd-440f-9602-6bdee004700f.89e4", value="#_swa_id#", domain="jam4.sapjam.com"},          
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

        script = script.replace('#_ct_remember#', config.JAM_COOKIE['_ct_remember'])
        script = script.replace('#_ct_session#', config.JAM_COOKIE['_ct_session'])
        script = script.replace('#_ct_sso#', config.JAM_COOKIE['_ct_sso'])
        script = script.replace('#_pk_id#', config.JAM_COOKIE['_pk_id'])
        script = script.replace('#_swa_id#', config.JAM_COOKIE['_swa_id'])

        # print(script)

        for item in self.start_urls:
            # yield scrapy.FormRequest(url, cookies=self.cookies, callback=self.parse)
            # 使用lua脚本，设置网关超时时间抓取网盘文件页面，设置meta传递id和抓取url
            # docker run -p 8050:8050 --name splash scrapinghub/splash --max-timeout 3600
            yield SplashRequest('https://' + config.DOMAIN + item['url'], callback=self.parse, endpoint='execute',
                                cache_args=['lua_source'],
                                args={'lua_source': script, 'timeout': 3600}, headers={'X-My-Header': 'value'},
                                meta={'id': item['id'], 'peoplename': item['display_name'], 'url': item['url']})

    def parse(self, response):
        item = JamScrapyProfileFollowItem()

        # 当前URL
        item['id'] = response.meta['id']
        item['peoplename'] = response.meta['peoplename']
        item['url'] = response.url
        # item['body'] = response.body_as_unicode()
        # unicode_body = response.body_as_unicode()  # 返回的html unicode编码

        # sel : 页面源代码
        result = scrapy.Selector(response)

        followers = result.xpath('//a[@name="followers"]/following-sibling::div[@class="profile_content"][1]'
                                 '//li[@class="teaser_list_item"]//div[@class="badgeDetails"]//a/text()').extract()
        follower_profiles = result.xpath('//a[@name="followers"]/following-sibling::div[@class="profile_content"][1]'
                                 '//li[@class="teaser_list_item"]//div[@class="badgeDetails"]//a/@href').extract()
        followings = result.xpath('//a[@name="following"]/following-sibling::div[@class="profile_content"][1]'
                                 '//li[@class="teaser_list_item"]//div[@class="badgeDetails"]//a/text()').extract()
        following_profiles = result.xpath('//a[@name="following"]/following-sibling::div[@class="profile_content"][1]'
                                 '//li[@class="teaser_list_item"]//div[@class="badgeDetails"]//a/@href').extract()

        if followers and follower_profiles and len(followers) == len(follower_profiles):
            json_followers = []
            for i in range(len(followers)):
                json_followers.append({'name': followers[i], 'url': follower_profiles[i]})
                item['followers'] = json.dumps(json_followers)

        if followings and following_profiles and len(followings) == len(following_profiles):
            json_followings = []
            for i in range(len(followings)):
                json_followings.append({'name': followings[i], 'url': following_profiles[i]})
                item['following'] = json.dumps(json_followings)

        yield item
