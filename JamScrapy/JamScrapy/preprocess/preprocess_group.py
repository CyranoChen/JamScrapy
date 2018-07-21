import scrapy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from JamScrapy import config
from JamScrapy.preprocess.entity import Group

KEYWORD = 'blockchain'


def process_groups_overview():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()
    results = engine.execute(f"SELECT * FROM spider_jam_post WHERE body <> '[]' AND keyword = '{KEYWORD}'"
                          f" AND baseurl like '%%groups%%' AND baseurl not like '%%sw_items%%'"
                          f" AND baseurl not like '%%documents%%' AND baseurl not like '%%events%%'")

    print(results.rowcount)

    for r in results:
        print(r.baseurl)

        html = scrapy.Selector(text=r.body)
        group_name = html.xpath('//div[@class="group-name"]/span/span/text()').extract()
        member_count = html.xpath('//div[@class="group-num-members jam-small-text"]/span/a/span/text()').extract()
        member_info_url = html.xpath('//div[@class="group-num-members jam-small-text"]/span/a/@href').extract()

        if len(group_name) > 0:
            print('group:', group_name[0], 'members:', member_count[0])
            print(member_info_url[0])

            obj = Group(groupname=group_name[0], membercount=int(member_count[0]),
                        memberinfourl=member_info_url[0], groupurl=r.url, keyword=KEYWORD)

            session.add(obj)

            for item in obj.__dict__.items():
                print(item)

    session.commit()


if __name__ == '__main__':
    process_groups_overview()
    print("All Done")
