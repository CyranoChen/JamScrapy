import scrapy
from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from JamScrapy import config
from JamScrapy.preprocess.entity import Post, People


def query_posts_by_category(category):
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()
    return session.query(Post).filter(and_(Post.url.like(f'%{category}%'), Post.body.isnot(None))).all()


def process_questions():
    posts = query_posts_by_category('questions')

    for p in posts:
        print(p.url)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath('//span[@class="jam-item-creator"]/a/text()').extract()
        creator_profiles = html.xpath('//span[@class="jam-item-creator"]/a/@href').extract()

        participators = html.xpath('//div[@class="feed-action-container"]/span/a/text()').extract()
        participator_profiles = html.xpath('//div[@class="feed-action-container"]/span/a/@href').extract()

        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        session = sessionmaker(bind=engine)()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(displayname=creators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=creator_profiles[index], roletype='creator')
                session.add(obj)

        print('participators:', participators)

        if len(participators) > 0:
            for index in range(len(participators)):
                obj = People(displayname=participators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=participator_profiles[index], roletype='participator')
                session.add(obj)

        session.commit()


def process_blogs():
    posts = query_posts_by_category('blogs')

    for p in posts:
        print(p.url)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/text()').extract()
        creator_profiles = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/@href').extract()

        participators = html.xpath('//div[@class="feed-action-container"]/span/a/text()').extract()
        participator_profiles = html.xpath('//div[@class="feed-action-container"]/span/a/@href').extract()

        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        session = sessionmaker(bind=engine)()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(displayname=creators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=creator_profiles[index], roletype='creator')
                session.add(obj)

        print('participators:', participators)

        if len(participators) > 0:
            for index in range(len(participators)):
                obj = People(displayname=participators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=participator_profiles[index], roletype='participator')
                session.add(obj)

        session.commit()


def process_discussions():
    posts = query_posts_by_category('discussions')

    for p in posts:
        print(p.url)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath('//span[@class="jam-item-creator"]/a[@id="content-member-badge"]/text()').extract()
        creator_profiles = html.xpath('//span[@class="jam-item-creator"]/a[@id="content-member-badge"]/@href').extract()

        participators = html.xpath('//div[@class="feed-comment-actor"]/a/text()').extract()
        participator_profiles = html.xpath('//div[@class="feed-comment-actor"]/a/@href').extract()

        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        session = sessionmaker(bind=engine)()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(displayname=creators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=creator_profiles[index], roletype='creator')
                session.add(obj)

        print('participators:', participators)

        if len(participators) > 0:
            for index in range(len(participators)):
                obj = People(displayname=participators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=participator_profiles[index], roletype='participator')
                session.add(obj)

        session.commit()


def process_wiki():
    posts = query_posts_by_category('wiki')

    for p in posts:
        print(p.url)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/text()').extract()
        creator_profiles = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/@href').extract()

        participators = html.xpath('//div[@class="feed-action-container"]/span/a/text()').extract()
        participator_profiles = html.xpath('//div[@class="feed-action-container"]/span/a/@href').extract()

        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        session = sessionmaker(bind=engine)()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(displayname=creators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=creator_profiles[index], roletype='creator')
                session.add(obj)

        print('participators:', participators)

        if len(participators) > 0:
            for index in range(len(participators)):
                obj = People(displayname=participators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=participator_profiles[index], roletype='participator')
                session.add(obj)

        session.commit()


def process_poll():
    posts = query_posts_by_category('poll')

    for p in posts:
        print(p.url)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath('//div[@class="poll-details"]/p[@class="time"]/a/text()').extract()
        creator_profiles = html.xpath('//div[@class="poll-details"]/p[@class="time"]/a/@href').extract()

        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        session = sessionmaker(bind=engine)()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(displayname=creators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=creator_profiles[index], roletype='creator')
                session.add(obj)

        session.commit()


def process_profile():
    posts = query_posts_by_category('profile')

    for p in posts:
        print(p.url)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/text()').extract()
        creator_profiles = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/@href').extract()

        participators = html.xpath('//div[@class="feed-action-container"]/span/a/text()').extract()
        participator_profiles = html.xpath('//div[@class="feed-action-container"]/span/a/@href').extract()

        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        session = sessionmaker(bind=engine)()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(displayname=creators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=creator_profiles[index], roletype='creator')
                session.add(obj)

        print('participators:', participators)

        if len(participators) > 0:
            for index in range(len(participators)):
                obj = People(displayname=participators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=participator_profiles[index], roletype='participator')
                session.add(obj)

        session.commit()


def process_feed():
    posts = query_posts_by_category('feed')

    for p in posts:
        print(p.url)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath('//div[@class="feed-action-container"]/span/a/text()').extract()
        creator_profiles = html.xpath('//div[@class="feed-action-container"]/span/a/@href').extract()

        participators = html.xpath('//div[@class="feed-comment-actor"]/a/text()').extract()
        participator_profiles = html.xpath('//div[@class="feed-comment-actor"]/a/@href').extract()

        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        session = sessionmaker(bind=engine)()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(displayname=creators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=creator_profiles[index], roletype='creator')
                session.add(obj)

        print('participators:', participators)

        if len(participators) > 0:
            for index in range(len(participators)):
                obj = People(displayname=participators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=participator_profiles[index], roletype='participator')
                session.add(obj)

        session.commit()


def process_ideas():
    posts = query_posts_by_category('ideas')

    for p in posts:
        print(p.url)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath('//span[@class="jam-item-creator"]/a/text()').extract()
        creator_profiles = html.xpath('//span[@class="jam-item-creator"]/a/@href').extract()

        participators = html.xpath('//div[@class="feed-action-container"]/span/a/text()').extract()
        participator_profiles = html.xpath('//div[@class="feed-action-container"]/span/a/@href').extract()

        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        session = sessionmaker(bind=engine)()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(displayname=creators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=creator_profiles[index], roletype='creator')
                session.add(obj)

        print('participators:', participators)

        if len(participators) > 0:
            for index in range(len(participators)):
                obj = People(displayname=participators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=participator_profiles[index], roletype='participator')
                session.add(obj)

        session.commit()


def process_groups_events():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()
    posts = session.query(Post).filter(and_(Post.baseurl.like('%groups%'), Post.baseurl.like('%events%'),
                                            Post.body.isnot(None))).all()

    print(len(posts))

    for p in posts:
        print(p.url)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/text()').extract()
        creator_profiles = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/@href').extract()

        participators = html.xpath('//div[@class="feed-action-container"]/span/a/text()').extract()
        participator_profiles = html.xpath('//div[@class="feed-action-container"]/span/a/@href').extract()

        # engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        # session = sessionmaker(bind=engine)()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(displayname=creators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=creator_profiles[index], roletype='creator')
                session.add(obj)

        print('participators:', participators)

        if len(participators) > 0:
            for index in range(len(participators)):
                obj = People(displayname=participators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=participator_profiles[index], roletype='participator')
                session.add(obj)

        session.commit()


def process_groups_documents():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()
    posts = session.query(Post).filter(and_(Post.baseurl.like('%groups%'), Post.baseurl.like('%documents%'),
                                            Post.body.isnot(None))).all()

    print(len(posts))

    for p in posts:
        print(p.url)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/text()').extract()
        creator_profiles = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/@href').extract()

        participators = html.xpath('//div[@class="feed-action-container"]/span/a/text()').extract()
        participator_profiles = html.xpath('//div[@class="feed-action-container"]/span/a/@href').extract()

        # engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        # session = sessionmaker(bind=engine)()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(displayname=creators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=creator_profiles[index], roletype='creator')
                session.add(obj)

        print('participators:', participators)

        if len(participators) > 0:
            for index in range(len(participators)):
                obj = People(displayname=participators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=participator_profiles[index], roletype='participator')
                session.add(obj)

        session.commit()


def process_groups_sw_items():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()
    posts = session.query(Post).filter(and_(Post.baseurl.like('%groups%'), Post.baseurl.like('%sw_items%'),
                                            Post.body.isnot(None))).all()

    print(len(posts))

    for p in posts:
        print(p.url)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/text()').extract()
        creator_profiles = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/@href').extract()

        participators = html.xpath('//div[@class="feed-action-container"]/span/a/text()').extract()
        participator_profiles = html.xpath('//div[@class="feed-action-container"]/span/a/@href').extract()

        # engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        # session = sessionmaker(bind=engine)()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(displayname=creators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=creator_profiles[index], roletype='creator')
                session.add(obj)

        print('participators:', participators)

        if len(participators) > 0:
            for index in range(len(participators)):
                obj = People(displayname=participators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=participator_profiles[index], roletype='participator')
                session.add(obj)

        session.commit()


def clean_up_participators():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()
    creators = session.query(People).filter(People.roletype == 'creator').all()

    print(len(creators))

    for c in creators:
        engine.execute(f'''update jam_people_from_post set position = -1  
        where postid = {c.postid} and displayname = \'{c.displayname}\' and roletype = \'participator\' ''')
        # print('postid:', c.postid, 'creator:', c.displayname, 'clean up:', len(results))

if __name__ == '__main__':
    # process_questions()
    # process_blogs()
    # process_discussions()
    # process_wiki()
    # process_poll()
    # process_profile()
    # process_feed()
    # process_ideas()
    # process_groups_events()
    # process_groups_documents()
    # process_groups_sw_items()
    clean_up_participators()

    print("All Done")
