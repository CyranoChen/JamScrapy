from JamScrapy import config
from sqlalchemy import create_engine, text

import scrapy

engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
result = engine.execute(
    text("SELECT * FROM spider_jam_profile WHERE id = :id"),
    {"id": 115041})

p = result.fetchone()


html = scrapy.Selector(text=p.body)
username = html.xpath('//div[@class="viewJobInfo"]/span[@class="profileLabel" and text()="User Name:"]/../text()').extract()
peoplename = html.xpath('//span[@class="member_name"]/text()').extract()

print(username)
print(peoplename[0].strip())

