import scrapy
from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from JamScrapy import config
from JamScrapy.preprocess.entity import Post, Group


def process_groups_overview():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()
    posts = session.query(Post).filter(and_(Post.baseurl.like('%groups%'), Post.baseurl.notlike('%sw_items%'),
                                            Post.baseurl.notlike('%documents%'), Post.baseurl.notlike('%events%'),
                                            Post.body.isnot(None))).all()

    print(len(posts))

    for p in posts:
        print(p.url)

        html = scrapy.Selector(text=p.body)
        group_name = html.xpath('//div[@class="group-name"]/span/span/text()').extract()
        member_count = html.xpath('//div[@class="group-num-members jam-small-text"]/span/a/span/text()').extract()
        member_info_url = html.xpath('//div[@class="group-num-members jam-small-text"]/span/a/@href').extract()

        if len(group_name) > 0:
            print('group:', group_name[0], 'members:', member_count[0])
            print(member_info_url[0])

            obj = Group(groupname=group_name[0], membercount=int(member_count[0]),
                        memberinfourl=member_info_url[0], groupurl=p.url)
            session.add(obj)

        session.commit()


if __name__ == '__main__':
    # process_groups_overview()
    print("All Done")
