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

    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    results = engine.execute('SELECT * FROM jam_profile order by id')

    # print(results.rowcount)

    for item in results:
        uid = item.profileurl.split("/")[-1]
        start_urls.append({'id': item.id, 'display_name': item.displayname, 'url': '/groups/view/' + uid})

    def start_requests(self):
        # 自行初始化设置cookie
        script = """        
        function main(splash)         
          splash:init_cookies({
            {name="_ct_remember", value="3be80cb227346380", domain="jam4.sapjam.com"},
            {name="_ct_session", value="ZnRnNmtPZlhzRHVabTR5SUY1OW1RNTlrdlBwaHErbHhWYnNTMmJ2ZTBUTVdjcGVuQVdNWW1lK21ralVMcWx5dUMxS3MrcFVKNTBGeDRtVm40UkE5aHl6cXYyc05oNlJQN0xoZVl0bFcyQlA3MXBYclY1TGtpWVpYZVBIUXdhcFdMLzRvOUZrcFQyenFvVHExTFBFT2tBcW8zY25aakVWeld1UFE5Wk9qei9wckxiMzA5emFXUUN0UnRDWUNpdHpPaDZNSlU5bG9lMm9PSUYwbEphZU5xUUZvOHBwQW5vK0I5TFc4OEgzQ0F5Ly9PU2xMN2F5cTBuVDJ5cXF1ZmhkNUxMM2V3QUhIdlJ5Y2RtYWd3TGp5eGo0bU9yWkMrT1pRM3kvblJWckhDMDR6VUJmUGdYZlFZN2ZQVHlYS0JvaTFIelpmUzE1dGpNcGdRNzg3R3h2cGUwRFZBaHU0T0lGeGpzekJwTDVDVmE3MW5EakRSUk5uZzF0WWprRFplVnk3endmOVJBTGJtNW1YY3NHZURoN0IraXoyOWxsbVpHRis3Z0lCQ2cwMEFBODgrTTBaZUtwR3o1WW5SQ3JKZFpwNDk4U0o2VWRvekFZTzdNaWhwT1JST25SOVdRNUxIS3pYMFdkZXFJY3VxQU9FWW9nRURUaHpPNVhmWERlQ05weWtOeElnNHhrcFhoSUxZYkZWeXR4a3luZG8xMy9JVHEyc3JOOUZDNDN4eHBFdmwzU2N4ckczNGdabXA2UDkyamltanF6VkgwR3BkSk1tdjBaOHdLUkU0K0NuNXNYZ1NZeW1CaUc2dm1wZWhKTkYwODVwcHVxREZyc0NIaGJlUThsUS0tZUpocGVHRjFxdGlNZ0lCdnhYQXZEZz09--a8fc9c0ee39a1f4de0eaab07852b536aa96a006b", domain="jam4.sapjam.com"},
            {name="_ct_sso", value="jamatsap.com", domain="jam4.sapjam.com"},
            {name="_pk_id.2bcdec4d-0cbd-440f-9602-6bdee004700f.89e4", value="ced4b00e4c1caa25.1522053703.0.1522053703..", domain="jam4.sapjam.com"},
            {name="_swa_id.2bcdec4d-0cbd-440f-9602-6bdee004700f.89e4", value="e0753f6a2aced465.1522053704.1.1522053704.1522053704.", domain="jam4.sapjam.com"},          
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

        for item in self.start_urls:
            # yield scrapy.FormRequest(url, cookies=self.cookies, callback=self.parse)
            # 使用lua脚本，设置网关超时时间抓取网盘文件页面，设置meta传递id和抓取url
            # docker run -p 8050:8050 --name splash scrapinghub/splash --max-timeout 3600
            yield SplashRequest('https://' + config.DOMAIN + item['url'], callback=self.parse, endpoint='execute',
                                cache_args=['lua_source'],
                                args={'lua_source': script, 'timeout': 3600}, headers={'X-My-Header': 'value'},
                                meta={'id': item['id'], 'peoplename': item['display_name'], 'url': item['url']})

    def parse(self, response):
        item = JamScrapyProfileGroupItem()

        # 当前URL
        item['id'] = response.meta['id']
        item['peoplename'] = response.meta['peoplename']
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
