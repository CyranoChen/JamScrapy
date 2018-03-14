from JamScrapy import config
from JamScrapy.preprocess.entity import Post, People

from sqlalchemy import create_engine
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker

import scrapy


def query_posts_by_category(category):
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()
    return session.query(Post).filter(and_(Post.url.like(f'%{category}%'), Post.body.isnot(None))).all()


def process_questions():
    posts = query_posts_by_category('questions')

    for p in posts:
        html = scrapy.Selector(text=p.body)
        creators = html.xpath('//span[@class="jam-item-creator"]/a/text()').extract()
        creator_profiles = html.xpath('//span[@class="jam-item-creator"]/a/@href').extract()

        repliers = html.xpath('//div[@class="feed-action-container"]/span/a/text()').extract()
        replier_profiles = html.xpath('//div[@class="feed-action-container"]/span/a/@href').extract()

        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        session = sessionmaker(bind=engine)()

        print(creators)

        if len(creators) > 0:
            for index in range(len(creators)):
                obj = People(displayname=creators[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=creator_profiles[index], roletype='creator')
                session.add(obj)

        print(repliers)

        if len(repliers) > 0:
            for index in range(len(repliers)):
                obj = People(displayname=repliers[index], postid=p.id, posturl=p.url, position=index,
                             profileurl=replier_profiles[index], roletype='replier')
                session.add(obj)

        session.commit()


def process_feeds():
    return True


if __name__ == '__main__':
    # process_questions()
    process_feeds()
