import scrapy

from sqlalchemy import create_engine
from JamScrapy.mysql import MySQL

from JamScrapy import config


def process():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

    results = engine.execute(f"SELECT * FROM spider_jam_post WHERE body <> '[]' AND keyword = 'people'")

    print(results.rowcount)

    db = MySQL()
    count = 0
    for r in results:
        html = scrapy.Selector(text=r.body)
        user_name = html.xpath('//div[@class="viewJobInfo"]/text()').extract()
        display_name = html.xpath('//span[@class="member_name"]/text()').extract()

        if user_name:
            user_name = user_name[0]
        else:
            user_name = ''

        if display_name:
            display_name = display_name[0]
        else:
            display_name = ''

        print(user_name, display_name)

        para = [db.escape_string(str(user_name)),
                db.escape_string(str(display_name)),
                db.escape_string(str(r.baseurl)),
                db.escape_string(str(r.body))]

        sql = f'insert into spider_jam_profile (username, peoplename, url, body, createtime, keyword) ' \
              f'values ("{para[0]}", "{para[1]}", "{para[2]}", "{para[3]}", NOW(), "people")'

        db.query(sql)

        count += 1
        if count % 1000 == 0:
            print(count)


if __name__ == '__main__':
    process()

    print("All Done")
