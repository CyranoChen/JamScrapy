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
    start_urls = engine.execute(
        'SELECT distinct displayname, profileurl FROM jam_people_from_post WHERE displayname <> \'Alumni\' ORDER BY displayname')

    def start_requests(self):
        # 自行初始化设置cookie
        script = """        
        function main(splash)         
          splash:init_cookies({
            {name="_ct_remember", value="2e1c74962797f53b", domain="jam4.sapjam.com"},
            {name="_ct_session", value="bWMrNmoyOWlMa2tNclRaS1J2MkFWVzVQZmRwNWgwSmJ3QjZlOXdsaWdnUHlkU0RFcDNTZXBkL2JnRXdwYlFKT00rTTl6MktaUFFSZldPWFFnUjdNZExyQ25rL2Z5WnJhMm9obkJmd2NFRXN5dGNPaDBzTU5PZU5PakU1S1lGUm43WlJCKzNadC8xK09qaHgweStuMjF1M2lVbmRRQ2tOVUNEVHVVenZ6ZmdQNXQvZWlmQkFGaG5JNWhZMEtXK2JrTFIwek1ERWFIczBhV2grbUQrRTlNQlBZaGswMU90akxKSFpnZVZWTDMvVmNkeFI5cGJRVzl3N2FBQ1I0WW1nR1Z3MzJ0ditCdDVzcnV0TW5KUHk2VzVRdDhTNGhVMko3YmRTNFV4aStyYmcwc0VaWTRnZlEwM3pPVVJ6b3dwK3FmVy8vaW9LQTk4eXNFM2ZwMTF6TU40Qk5CaHZVYm9pYnRwUEphWXVuNzVzM1o0THVzQkdDT2hlWjRWTEdJUDFTazJNQUFNVFVrUE1xNDNpdms0bGpvSHdPaUQvekY4VVJ1VVlYS0pyWXpnbGIzbTMzVVRCOWpZaUlOTTlrMjJIdTJhNGhNUUZQMnFqanZjaWNvTUhJQXIrZUVqd1BMQXNUMmJpTWRlNEllZDZQaDNSUGg5eHhYYmNEdHowQnVnQzVYVlp3QnVleWdkKzVPZDZsVm5ya2ZJYU1LSW03Mk42aGNBd2Fic1g3bVZ0SVdmK3AwZ2g4T0hXNXM2SUwyVWJBTlFLTTdidHZ4MW9La2JFbHZRTTlFeC90RG9lSmVpdWdLOHJKenRnejdTVDFjR3JnL1dWVHhjQ0ZZWExXZEdUWi0tOXd5dmlsWTZyM3NJZEpQeFBNcTZHZz09--bcad31f07d2654fb05de314967d11177c1c2690d", domain="jam4.sapjam.com"},
            {name="_ct_sso", value="jamatsap.com", domain="jam4.sapjam.com"},
            {name="_pk_id.2bcdec4d-0cbd-440f-9602-6bdee004700f.89e4", value="b0e1d1fb99b1d8cf.1520824691.0.1520824691..", domain="jam4.sapjam.com"},
            {name="_swa_id.2bcdec4d-0cbd-440f-9602-6bdee004700f.89e4", value="8efc22dbd171026d.1520824691.1.1520824692.1520824691.", domain="jam4.sapjam.com"},          
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
            # 使用lua脚本，设置网关超时时间抓取网盘文件页面，设置meta传递id和抓取url
            # docker run -p 8050:8050 --name splash scrapinghub/splash --max-timeout 3600
            yield SplashRequest('https://' + config.DOMAIN + url[1], callback=self.parse, endpoint='execute',
                                cache_args=['lua_source'],
                                args={'lua_source': script, 'timeout': 3600}, headers={'X-My-Header': 'value'},
                                meta={'peoplename': url[0], 'url': url[1]})

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
