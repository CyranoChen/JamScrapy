#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
from glob import glob, iglob

import scrapy
from scrapy_splash import SplashRequest

from JamScrapy.items import PortalSuccessFactorsItem


class PortalSuccessFactorsSpider(scrapy.Spider):
    # 爬虫名称
    name = "PortalSuccessFactorsSpider"
    # 设置下载延时, 避免被BAN
    download_delay = 5
    # 允许域名
    allowed_domains = ['performancemanager5.successfactors.eu', 'mediaservicesfmsprod.ms.successfactors.com']
    sf_avatar_path = './data/avatar/sf/'
    sf_profile_url = 'https://performancemanager5.successfactors.eu/sf/liveprofile?#/user/'

    request_urls = []

    def start_requests(self):
        for fp in iglob(self.sf_avatar_path + '**', recursive=True):
            if os.path.isfile(fp):
                sf_id = str(fp.strip(self.sf_avatar_path).strip('.jpg'))
                self.request_urls.append(sf_id)

        print(self.name, len(self.request_urls))

        # cookies = {
        #     'BIGipServermediaservicesfmsprod.ms.successfactors.com': '587222538.26911.0000',
        #     'JSESSIONID': '62A46BCE3C7B4E65A39C93A5D629FBF9.vsa3757013',
        #     'assertingPartyCookieKey': 'SAP_Prod_NewSAML20_20130409',
        #     'bizxThemeId': 'blueCrystalInterior',
        #     'loginMethodCookieKey': 'SSO',
        #     'route': '46d634bc3a5797b19bd0bd06fb917cc39f41f93e',
        #     'zsessionid': 'dca4725f-4a57-49a4-bd33-2a008ea272e5',
        # }

        # 自行初始化设置cookie
        script = """        
        function main(splash)         
          splash:init_cookies({
            {name="BIGipServermediaservicesfmsprod.ms.successfactors.com", value="587222538.26911.0000", domain="mediaservicesfmsprod.ms.successfactors.com"},
            {name="JSESSIONID", value="62A46BCE3C7B4E65A39C93A5D629FBF9.vsa3757013", domain="performancemanager5.successfactors.eu"},  
            {name="assertingPartyCookieKey", value="SAP_Prod_NewSAML20_20130409", domain="performancemanager5.successfactors.eu"},
            {name="bizxThemeId", value="blueCrystalInterior", domain="performancemanager5.successfactors.eu"},
            {name="loginMethodCookieKey", value="SSO", domain="performancemanager5.successfactors.eu"},
            {name="route", value="46d634bc3a5797b19bd0bd06fb917cc39f41f93e", domain="performancemanager5.successfactors.eu"},
            {name="zsessionid", value="dca4725f-4a57-49a4-bd33-2a008ea272e5", domain="performancemanager5.successfactors.eu"}     
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
        # https://performancemanager5.successfactors.eu/sf/liveprofile?#/user/15274
        # https://performancemanager5.successfactors.eu/sf/liveprofile?selected_user=161590
        for sf_id in self.request_urls:
            # yield scrapy.FormRequest(url, cookies=self.cookies, callback=self.parse)
            # 使用lua脚本，设置网关超时时间抓取网盘文件页面，设置meta传递id和抓取url
            # docker run -p 8050:8050 --name splash scrapinghub/splash --max-timeout 3600
            yield SplashRequest(self.sf_profile_url + sf_id, callback=self.parse,
                                endpoint='execute',
                                cache_args=['lua_source'],
                                args={'lua_source': script, 'timeout': 3600, 'wait': 15},
                                headers={'X-My-Header': 'value'},
                                meta={'id': sf_id})

    def parse(self, response):
        item = PortalSuccessFactorsItem()

        # 当前URL
        item['id'] = response.meta['id']
        item['url'] = response.url
        item['body'] = response.body_as_unicode()

        # sel : 页面源代码
        result = scrapy.Selector(response)
        # item['body'] = result.xpath('//table[@class="sapExtentUilibFormPatternTable"]').extract()

        yield item
