import scrapy
from JamScrapy import config
from sqlalchemy import create_engine

engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
profiles = engine.execute("select * from spider_jam_profile where username not like 'c%%' and username not like 'd%%' and username not like 'i%%' ")

print('profiles', profiles.rowcount)

for p in profiles:
    print(p.id, p.peoplename)

    html = scrapy.Selector(text=p.body)
    user_name = html.xpath('//div[@class="viewJobInfo"]/text()').extract()

    print(user_name[2])

    engine.execute(f"update spider_jam_profile set username = '{user_name[2].strip()}' where id = {p.id}")

