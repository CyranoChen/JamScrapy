from tqdm import tqdm
import scrapy
from sqlalchemy import and_
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from JamScrapy import config
from JamScrapy.preprocess.entity import People

KEYWORD = config.KEYWORD
PROFILES = dict()
SET_EXISTURLS = set()


def query_posts_by_category(category):
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

    result = engine.execute(
        f"SELECT distinct baseurl, id, body FROM spider_jam_post WHERE keyword = '{KEYWORD}'"
        f" AND baseurl like '%%{category}%%' AND url not like '%%deleted%%'")

    # 过滤掉已存在的url
    filter_result = []
    for r in result:
        if r.baseurl.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', '') in SET_EXISTURLS:
            continue

        filter_result.append(r)

    print(category, result.rowcount, len(filter_result))

    return filter_result


def initial_profiles():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

    results = engine.execute(f"select profileurl, username from people_profile")

    for r in results:
        url = r.profileurl.split('/')[-1]
        PROFILES[url] = r.username.strip()


def initial_exist_urls():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

    results = engine.execute(f"select distinct posturl from jam_people_from_post where keyword = '{KEYWORD}'")

    for r in results:
        SET_EXISTURLS.add(r.posturl.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', ''))

    print('SET_EXISTURLS', len(SET_EXISTURLS))


def get_people_username(profileurl):
    url = profileurl.split('/')[-1]

    if len(PROFILES) > 0 and url in PROFILES.keys():
        return PROFILES[url]
    else:
        return ''


def process_questions():
    posts = query_posts_by_category('questions')

    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()

    for p in posts:
        print(p.baseurl)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath('//span[@class="jam-item-creator"]/a/text()').extract()
        creator_profiles = html.xpath('//span[@class="jam-item-creator"]/a/@href').extract()

        participators = html.xpath('//div[@class="feed-action-container"]/span/a/text()').extract()
        participator_profiles = html.xpath('//div[@class="feed-action-container"]/span/a/@href').extract()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(username=get_people_username(creator_profiles[index]), displayname=creators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=creator_profiles[index], roletype='creator', keyword=KEYWORD)
                session.add(obj)

        print('participators:', participators)

        if len(participators) > 0:
            for index in range(len(participators)):
                obj = People(username=get_people_username(participator_profiles[index]),
                             displayname=participators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=participator_profiles[index], roletype='participator', keyword=KEYWORD)
                session.add(obj)

    session.commit()


def process_blogs():
    posts = query_posts_by_category('blogs')

    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()

    for p in posts:
        print(p.baseurl)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/text()').extract()
        creator_profiles = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/@href').extract()

        participators = html.xpath('//div[@class="feed-action-container"]/span/a/text()').extract()
        participator_profiles = html.xpath('//div[@class="feed-action-container"]/span/a/@href').extract()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(username=get_people_username(creator_profiles[index]), displayname=creators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=creator_profiles[index], roletype='creator', keyword=KEYWORD)
                session.add(obj)

        print('participators:', participators)

        if len(participators) > 0:
            for index in range(len(participators)):
                obj = People(username=get_people_username(participator_profiles[index]),
                             displayname=participators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=participator_profiles[index], roletype='participator', keyword=KEYWORD)
                session.add(obj)

    session.commit()


def process_discussions():
    posts = query_posts_by_category('discussions')

    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()

    for p in posts:
        print(p.baseurl)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath('//span[@class="jam-item-creator"]/a[@id="content-member-badge"]/text()').extract()
        creator_profiles = html.xpath('//span[@class="jam-item-creator"]/a[@id="content-member-badge"]/@href').extract()

        participators = html.xpath('//div[@class="feed-comment-actor"]/a/text()').extract()
        participator_profiles = html.xpath('//div[@class="feed-comment-actor"]/a/@href').extract()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(username=get_people_username(creator_profiles[index]), displayname=creators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=creator_profiles[index], roletype='creator', keyword=KEYWORD)
                session.add(obj)

        print('participators:', participators)

        if len(participators) > 0:
            for index in range(len(participators)):
                obj = People(username=get_people_username(participator_profiles[index]),
                             displayname=participators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=participator_profiles[index], roletype='participator', keyword=KEYWORD)
                session.add(obj)

    session.commit()


def process_wiki():
    posts = query_posts_by_category('wiki')

    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()

    for p in posts:
        print(p.baseurl)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/text()').extract()
        creator_profiles = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/@href').extract()

        participators = html.xpath('//div[@class="feed-action-container"]/span/a/text()').extract()
        participator_profiles = html.xpath('//div[@class="feed-action-container"]/span/a/@href').extract()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(username=get_people_username(creator_profiles[index]), displayname=creators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=creator_profiles[index], roletype='creator', keyword=KEYWORD)
                session.add(obj)

        print('participators:', participators)

        if len(participators) > 0:
            for index in range(len(participators)):
                obj = People(username=get_people_username(participator_profiles[index]),
                             displayname=participators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=participator_profiles[index], roletype='participator', keyword=KEYWORD)
                session.add(obj)

    session.commit()


def process_articles():
    posts = query_posts_by_category('articles')

    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()

    for p in posts:
        print(p.baseurl)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/text()').extract()
        creator_profiles = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/@href').extract()

        participators = html.xpath('//div[@class="feed-action-container"]/span/a/text()').extract()
        participator_profiles = html.xpath('//div[@class="feed-action-container"]/span/a/@href').extract()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(username=get_people_username(creator_profiles[index]), displayname=creators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=creator_profiles[index], roletype='creator', keyword=KEYWORD)
                session.add(obj)

        print('participators:', participators)

        if len(participators) > 0:
            for index in range(len(participators)):
                obj = People(username=get_people_username(participator_profiles[index]),
                             displayname=participators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=participator_profiles[index], roletype='participator', keyword=KEYWORD)
                session.add(obj)

    session.commit()


def process_poll():
    posts = query_posts_by_category('poll')

    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()

    for p in posts:
        print(p.baseurl)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath('//div[@class="poll-details"]/p[@class="time"]/a/text()').extract()
        creator_profiles = html.xpath('//div[@class="poll-details"]/p[@class="time"]/a/@href').extract()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(username=get_people_username(creator_profiles[index]), displayname=creators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=creator_profiles[index], roletype='creator', keyword=KEYWORD)
                session.add(obj)

    session.commit()


def process_profile():
    posts = query_posts_by_category('profile')

    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()

    for p in posts:
        print(p.baseurl)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath('//span[@class="member_name"]/text()').extract()
        creator_profiles = p.baseurl.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', '')

        # participators = html.xpath('//div[@class="feed-action-container"]/span/a/text()').extract()
        # participator_profiles = html.xpath('//div[@class="feed-action-container"]/span/a/@href').extract()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(username=get_people_username(creator_profiles[index]), displayname=creators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=creator_profiles[index], roletype='creator', keyword=KEYWORD)
                session.add(obj)

    session.commit()


def process_feed():
    posts = query_posts_by_category('feed')

    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()

    for p in posts:
        print(p.baseurl)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath('//div[@class="feed-action-container"]/span/span/a/text()').extract()
        creator_profiles = html.xpath('//div[@class="feed-action-container"]/span/span/a/@href').extract()

        participators = html.xpath('//div[@class="inline-action"]/a/text()').extract()
        participator_profiles = html.xpath('//div[@class="inline-action"]/a/@href').extract()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(username=get_people_username(creator_profiles[index]), displayname=creators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=creator_profiles[index], roletype='creator', keyword=KEYWORD)
                session.add(obj)

        print('participators:', participators)

        if len(participators) > 0:
            for index in range(len(participators)):
                obj = People(username=get_people_username(participator_profiles[index]),
                             displayname=participators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=participator_profiles[index], roletype='participator', keyword=KEYWORD)
                session.add(obj)

    session.commit()


def process_ideas():
    posts = query_posts_by_category('ideas')

    for p in posts:
        print(p.baseurl)

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
                obj = People(username=get_people_username(creator_profiles[index]), displayname=creators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=creator_profiles[index], roletype='creator', keyword=KEYWORD)
                session.add(obj)

        print('participators:', participators)

        if len(participators) > 0:
            for index in range(len(participators)):
                obj = People(username=get_people_username(participator_profiles[index]),
                             displayname=participators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=participator_profiles[index], roletype='participator', keyword=KEYWORD)
                session.add(obj)

    session.commit()


def process_groups_events():
    posts = query_posts_by_category('events')

    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()

    for p in posts:
        print(p.baseurl)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/text()').extract()
        creator_profiles = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/@href').extract()

        participators = html.xpath('//div[@class="feed-action-container"]/span/a/text()').extract()
        participator_profiles = html.xpath('//div[@class="feed-action-container"]/span/a/@href').extract()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(username=get_people_username(creator_profiles[index]), displayname=creators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=creator_profiles[index], roletype='creator', keyword=KEYWORD)
                session.add(obj)

        print('participators:', participators)

        if len(participators) > 0:
            for index in range(len(participators)):
                obj = People(username=get_people_username(participator_profiles[index]),
                             displayname=participators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=participator_profiles[index], roletype='participator', keyword=KEYWORD)
                session.add(obj)

    session.commit()


def process_groups_documents():
    posts = query_posts_by_category('documents')

    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()

    for p in posts:
        print(p.baseurl)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/text()').extract()
        creator_profiles = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/@href').extract()

        participators = html.xpath('//div[@class="feed-action-container"]/span/a/text()').extract()
        participator_profiles = html.xpath('//div[@class="feed-action-container"]/span/a/@href').extract()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(username=get_people_username(creator_profiles[index]), displayname=creators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=creator_profiles[index], roletype='creator', keyword=KEYWORD)
                session.add(obj)

        print('participators:', participators)

        if len(participators) > 0:
            for index in range(len(participators)):
                obj = People(username=get_people_username(participator_profiles[index]),
                             displayname=participators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=participator_profiles[index], roletype='participator', keyword=KEYWORD)
                session.add(obj)

    session.commit()


def process_groups_sw_items():
    posts = query_posts_by_category('sw_items')

    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()

    for p in posts:
        print(p.baseurl)

        html = scrapy.Selector(text=p.body)
        creators = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/text()').extract()
        creator_profiles = html.xpath(
            '//div[@class="jam-content-item-meta jam-small-text"]/a[@id="content-member-badge"]/@href').extract()

        participators = html.xpath('//div[@class="feed-action-container"]/span/a/text()').extract()
        participator_profiles = html.xpath('//div[@class="feed-action-container"]/span/a/@href').extract()

        print('creators:', creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(username=get_people_username(creator_profiles[index]), displayname=creators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=creator_profiles[index], roletype='creator', keyword=KEYWORD)
                session.add(obj)

        print('participators:', participators)

        if len(participators) > 0:
            for index in range(len(participators)):
                obj = People(username=get_people_username(participator_profiles[index]),
                             displayname=participators[index],
                             postid=p.id, posturl=p.baseurl, position=index,
                             profileurl=participator_profiles[index], roletype='participator', keyword=KEYWORD)
                session.add(obj)

    session.commit()


def clean_up_participators():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()
    creators = session.query(People).filter(and_(People.roletype == 'creator', People.keyword == KEYWORD)).all()

    print("creators", len(creators))

    if len(creators) > 0:
        for c in tqdm(creators):
            engine.execute(f'''update jam_people_from_post set position = -1  
                        where postid = {c.postid} and username = \'{c.username}\' and roletype = \'participator\' ''')
            # print('postid:', c.postid, 'creator:', c.displayname, 'clean up:', len(results))


def fill_postid():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    results = engine.execute(f"select id, url from jam_post where keyword = '{KEYWORD}'").fetchall()

    print('jam_posts:', len(results))

    post_dict = dict()
    for r in results:
        url = r.url.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', '')
        post_dict[url] = r.id

    results = engine.execute(
        f"select id, posturl, postid from jam_people_from_post where keyword = '{KEYWORD}'").fetchall()

    print('jam_people_from_posts:', len(results))

    if len(results) > 0:
        for r in tqdm(results):
            url = r.posturl.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', '')
            if url in post_dict:
                postid = post_dict[url]
                if postid != r.postid:
                    engine.execute(text("update jam_people_from_post set postid=:postid where id = :id"),
                                   {"postid": postid, "id": r.id})


if __name__ == '__main__':
    initial_profiles()
    initial_exist_urls()

    process_questions()
    process_blogs()
    process_discussions()
    process_wiki()
    process_articles()
    process_poll()
    process_profile()
    process_feed()
    process_ideas()
    process_groups_events()
    process_groups_documents()
    process_groups_sw_items()

    fill_postid()
    clean_up_participators()

    print("All Done")
