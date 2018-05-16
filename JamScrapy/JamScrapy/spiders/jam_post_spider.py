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
    start_urls = []

    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    results = engine.execute(f"select * from spider_jam_post where body = '[]' and keyword = 'blockchain'")
    # print(name, results.rowcount)

    start_urls = []

    # for r in results:
    #     start_urls.extend(ast.literal_eval(r.topics))

    def start_requests(self):
        # 自行初始化设置cookie
        script = """        
        function main(splash)         
          splash:init_cookies({
            {name="_ct_remember", value="2889fcb20d521b83", domain="jam4.sapjam.com"},
            {name="_ct_session", value="bVRLdDlnN3NBWkRFZ05kWnFPbTkrZktFRm5xb1UydkZPTW1LL1JlNkViVHNja1VmU2Q1dXVMK3JSNlJ5Lzg1aXlMUU9zeWlsOGdjWDY3bDBGQU9JSUw5MjJhbTkwRExoVTk4c0FvNkdZVWREVjZBYWQvdHJjNDF2N1Q1UTFqa05jY0ZiYmpYbEF5UVYybmdXMW5tM3ZuTkswdDZaKzdwbVB1dFVsc1RlN0dwbVROODAzc0NtNHQvNDRWS3hXb3VBdXZJOUhFOXVLSDR4M21XUjhHWXc4SzNNd0NBTmFMZzFva0NQNmNETnRHc1NhQWFLZldWWXNQU1I3TTUrTXppNmU1TGw3dFllaFVybmF5L1ZkcnhyT2ZXWVJqZW9qNjRQM0haa3RqYU4yRVBhcXZXMHMrUkxjZ0J3SVl1eWZwOU1lbDlmU1FOK1hidjBvVk14VmJKVlUvRUUvMERYd2trRUh3emhNN2UxUVhPUnhoRmlGeWNUNTRFSHRYVUJEWEprbWE5WkxTNElzbDRabjFkakdlQmpTOUkrWHgxRnRQK3dWVUtjYmNJaWVXTXVWeXIvTGFCLzV3cVpEaVRnS0licGFTWk9TNUsyaW56c2pldWlKaDZwTVB5NTlHN2xXV2U5UG1QY1dNL3JVOEF2eDFCVFl4MUZzQ3IxRlpmSmxLdUl1NCtMcGJTNTB0WE1jczlIOVQzc21wUTFQSFlNTjVsR1Y4UDB3cTgxdlZFYmZTendyK2syMnlFTkkzaVo0MFFqRXhQcTBneFhWNzEyYnp1enB6RmxJUE1oTC9ZZU9YRitQTzBCSFF6U3RhZHVBV0d6QXFIZlFLbktqNERDYTNvOS0tbHlNRDRFTVZIc1BuTmJCMEFqQmowQT09--383d0537ecc59bed8cb321f3122e4f3836ba106a", domain="jam4.sapjam.com"},
            {name="_ct_sso", value="jamatsap.com", domain="jam4.sapjam.com"},
            {name="_pk_id.2bcdec4d-0cbd-440f-9602-6bdee004700f.89e4", value="073c5e6fa9ebae9a.1522726660.0.1522726660..", domain="jam4.sapjam.com"},
            {name="_swa_id.2bcdec4d-0cbd-440f-9602-6bdee004700f.89e4", value="dd65c29bb6b360bc.1522726660.1.1522726729.1522726660.", domain="jam4.sapjam.com"},          
            {name="_swa_ref.2bcdec4d-0cbd-440f-9602-6bdee004700f.89e4", value="%5B%22%22%2C%22%22%2C1522726660%2C%22https%3A%2F%2Faccounts.sap.com%2Fsaml2%2Fidp%2Fsso%2Faccounts.sap.com%3FSAMLRequest%3DnVNdb9owFP0rkd8hhtCkswgShUlD7bYI0j7sBTn2TZstsT1fh9J%2FXydAhbSV%5CnBx4sS75f55x7PEXe1IbNW%2Fei1vC3BXTBvqkVsj6QktYqpjlWyBRvAJkTbDP%2F%5Cn%2FsDGQ8qM1U4LXZNgtUyJgPjmlo%2FGwMUoomWcFONExMlICioLmciYQlkWnMeU%5CnBE9gsdIqJb6Nr0ZsYaXQceX8Ex3dDuhkQKOcRixKWER%2FkSA7zrqrlKzU82Vg%5CnxSEJ2bc8zwbZz01OgjkiWOeHLrTCtgG7AburBDyuH1Ly4pxBFoa%2FeTMZIjf%2B%5CnHgrdhJ0IIZqQCyTB0otTKe564KcKLoRulcOu6qNkHFbShIj6nzCZTbsE1lO2%5CnZ1JfJsRP4MnsM6j%2BGK7e%2BvnbWgteb%2FHAcOv3tKsk2HB1T%2B%2FM89PXL%2Fc3j4JO%5Cn1J%2BdkWUxDc8gHfAZ9sNjWC0zXVfi7RpHzOtavy4scAcpcbYFEp5aH30Gsned%5CnX4eD%2FVWuW3SUbYXdPmDPhTupe954UXvx1lBeo%2FXFNMFE19o%2FZ%2F561VZ2HgXh%5CnieWWKzTauqO0%2F8MzO8Q%2BkeMjev4zZ%2B8%3D%5Cn%22%5D", domain="jam4.sapjam.com"},
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
            yield SplashRequest(r.baseurl, callback=self.parse, endpoint='execute', cache_args=['lua_source'],
                                args={'lua_source': script, 'timeout': 3600}, headers={'X-My-Header': 'value'},
                                meta={'id': r.id, 'baseurl': r.baseurl})

    def parse(self, response):
        item = JamScrapyPostItem()

        # 当前URL
        item['id'] = response.meta['id']
        item['baseurl'] = response.meta['baseurl']
        item['url'] = response.url
        # item['body'] = response.body_as_unicode()
        # unicode_body = response.body_as_unicode()  # 返回的html unicode编码

        # sel : 页面源代码
        result = scrapy.Selector(response)

        item['body'] = result.xpath('//div[@id="jam-layout"]').extract()

        yield item
