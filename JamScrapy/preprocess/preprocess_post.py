import scrapy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import json

from JamScrapy import config
from JamScrapy.preprocess.entity import Post

KEYWORD = 'blockchain'


def query_posts_by_category(category):
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

    return engine.execute(f"SELECT * FROM spider_jam_post WHERE body <> '[]' AND keyword = '{KEYWORD}'"
                          f" AND baseurl like '%%{category}%%' AND url not like '%%deleted%%'")


def init_post(url, category, keyword, title=None, author=None, recency=None, tags=None,
              content=None, comments=None, likes=None, views=None):
    p = Post()
    p.url = url
    p.category = category
    p.keyword = keyword

    if title:
        p.title = title[0]

    if author:
        p.author = author[0]

    if recency:
        p.recency = recency[0]

    if content:
        p.content = content[0]

    if tags:
        p.tag = json.dumps(tags)

    if comments:
        p.comments = int(comments)

    if likes:
        p.likes = int(likes)

    if views:
        p.views = int(views[0])

    return p


def count_likes(post_likes, feeds_likes):
    likes = 0

    if post_likes:
        for item in post_likes:
            likes += int(item)

    if feeds_likes:
        for item in feeds_likes:
            likes += int(item)

    return likes


def count_comments(post_comments, feeds_comments):
    comments = 0

    if post_comments:
        comments += len(post_comments)

    if feeds_comments:
        for item in feeds_comments:
            comments += int(item)

    return comments


def process_questions():
    results = query_posts_by_category('questions')

    for r in results:
        print(r.url)

        html = scrapy.Selector(text=r.body)

        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        session = sessionmaker(bind=engine)()

        title = html.xpath('//div[@class="jam-item-name"]/text()').extract()
        author = html.xpath('//span[@class="jam-item-creator"]/a/text()').extract()
        recency = html.xpath('//span[@class="jam-item-last-updated"]/span[@class="time"]/@timestamp').extract()
        tags = html.xpath('//div[@class="tags"]/div/a/text()').extract()
        content = html.xpath('//div[@class="wiki_content"]').extract()

        # shares

        post_comments = html.xpath('//div[@id="feed-list-container"]//'
                                   'div[@class="feed-action-container"]/span/a/text()').extract()
        feeds_comments = html.xpath('//div[@id="feed-list-container"]//'
                                    'span[@class="feed-comments-count-container feed-meta"]/@data-count').extract()

        # rates

        post_likes = html.xpath('//td[@class="metadata_label content-like-total"]/'
                                'following-sibling::td[@class="metadata_value"]/a/span/text()').extract()
        feeds_likes = html.xpath('//code[@class="feed-likes"]/@data-count').extract()

        views = html.xpath('//td[@class="metadata_label content-views"]/'
                           'following-sibling::td[@class="metadata_value"]/span/text()').extract()

        p = init_post(url=r.baseurl, category='questions', keyword=KEYWORD, title=title, author=author, recency=recency,
                      tags=tags, content=content, comments=count_comments(post_comments, feeds_comments),
                      likes=count_likes(post_likes, feeds_likes), views=views)

        session.add(p)

        for item in p.__dict__.items():
            print(item)

        session.commit()


def process_blogs():
    results = query_posts_by_category('blogs')

    for r in results:
        print(r.url)

        html = scrapy.Selector(text=r.body)

        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        session = sessionmaker(bind=engine)()

        title = html.xpath('//div[@id="content_title"]/text()').extract()
        author = html.xpath('//span[@class="jam-item-creator"]/a/text()').extract()
        recency = html.xpath('//span[@class="jam-item-last-updated"]/span[@class="time"]/@timestamp').extract()
        tags = html.xpath(
            '//div[@class="content-meta-container jam-flex wrap"]//span[@class="tag-token"]/a/@title').extract()
        content = html.xpath('//div[@class="content"]').extract()

        # shares

        post_comments = html.xpath('//span[@class="sap-icon icon-comment"]/span/text()').extract()
        feeds_comments = html.xpath('//div[@id="feed-list-container"]//'
                                    'span[@class="feed-comments-count-container feed-meta"]/@data-count').extract()

        # rates

        post_likes = html.xpath(
            '//span[@class="jam-item-likes"]//a[@class="metadata_value jam-clickable"]/@data-count').extract()
        feeds_likes = html.xpath('//code[@class="feed-likes"]/@data-count').extract()

        views = html.xpath('//span[@class="jam-item-views"]//a[@class="metadata_value "]/@data-count').extract()

        p = init_post(url=r.baseurl, category='blogs', keyword=KEYWORD, title=title, author=author, recency=recency,
                      tags=tags, content=content, comments=count_comments(post_comments, feeds_comments),
                      likes=count_likes(post_likes, feeds_likes), views=views)

        session.add(p)

        for item in p.__dict__.items():
            print(item)

        session.commit()


def process_discussions():
    results = query_posts_by_category('discussions')

    for r in results:
        print(r.url)

        html = scrapy.Selector(text=r.body)

        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        session = sessionmaker(bind=engine)()

        title = html.xpath('//div[@class="jam-item-name"]/text()').extract()
        author = html.xpath('//span[@class="jam-item-creator"]/a/text()').extract()
        recency = html.xpath('//span[@class="jam-item-last-updated"]/span[@class="time"]/@timestamp').extract()
        tags = html.xpath('//div[@class="tags"]/div/a/text()').extract()
        content = html.xpath('//div[@class="wiki_content"]').extract()

        # shares

        post_comments = html.xpath('//div[@id="feed-list-container"]//'
                                   'div[@class="feed-action-container"]/span/a/text()').extract()
        feeds_comments = html.xpath('//div[@id="feed-list-container"]//'
                                    'span[@class="feed-comments-count-container feed-meta"]/@data-count').extract()

        # rates

        post_likes = html.xpath('//td[@class="metadata_label content-like-total"]/'
                                'following-sibling::td[@class="metadata_value"]/a/span/text()').extract()
        feeds_likes = html.xpath('//code[@class="feed-likes"]/@data-count').extract()

        views = html.xpath('//td[@class="metadata_label content-views"]/'
                           'following-sibling::td[@class="metadata_value"]/span/text()').extract()

        p = init_post(url=r.baseurl, category='discussions', keyword=KEYWORD, title=title, author=author,
                      recency=recency,
                      tags=tags, content=content, comments=count_comments(post_comments, feeds_comments),
                      likes=count_likes(post_likes, feeds_likes), views=views)

        session.add(p)

        for item in p.__dict__.items():
            print(item)

        session.commit()


def process_wiki():
    results = query_posts_by_category('wiki')

    for r in results:
        print(r.url)

        html = scrapy.Selector(text=r.body)

        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        session = sessionmaker(bind=engine)()

        title = html.xpath('//div[@id="content_title"]/text()').extract()
        author = html.xpath('//span[@class="jam-item-creator"]/a/text()').extract()
        recency = html.xpath('//span[@class="jam-item-last-updated"]/span[@class="time"]/@timestamp').extract()
        tags = html.xpath(
            '//div[@class="content-meta-container jam-flex wrap"]//span[@class="tag-token"]/a/@title').extract()
        content = html.xpath('//div[@class="wiki_content"]').extract()

        # shares

        post_comments = html.xpath('//span[@class="sap-icon icon-comment"]/span/text()').extract()
        feeds_comments = html.xpath('//div[@id="feed-list-container"]//'
                                    'span[@class="feed-comments-count-container feed-meta"]/@data-count').extract()

        # rates

        post_likes = html.xpath(
            '//span[@class="jam-item-likes"]//a[@class="metadata_value jam-clickable"]/@data-count').extract()
        feeds_likes = html.xpath('//code[@class="feed-likes"]/@data-count').extract()

        views = html.xpath('//span[@class="jam-item-views"]//a[@class="metadata_value "]/@data-count').extract()

        p = init_post(url=r.baseurl, category='wiki', keyword=KEYWORD, title=title, author=author, recency=recency,
                      tags=tags, content=content, comments=count_comments(post_comments, feeds_comments),
                      likes=count_likes(post_likes, feeds_likes), views=views)

        session.add(p)

        for item in p.__dict__.items():
            print(item)

        session.commit()


def process_poll():
    results = query_posts_by_category('poll')

    for r in results:
        print(r.url)

        html = scrapy.Selector(text=r.body)

        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        session = sessionmaker(bind=engine)()

        title = html.xpath('//div[@id="content_title"]/text()').extract()
        author = html.xpath('//div[@class="poll-details"]/p[@class="time"]/a/text()').extract()
        recency = html.xpath('//div[@class="poll-details"]/p[@class="time"]/span[@class="time"]/@timestamp').extract()
        # tags
        content = html.xpath('//div[@class="poll-stats"]').extract()

        views = html.xpath('//div[@class="poll-responses"]/span/text()').extract()

        polls = 0

        if views:
            polls = views[0].replace(' Responses.', '')

        p = init_post(url=r.baseurl, category='poll', keyword=KEYWORD, title=title, author=author, recency=recency,
                      content=content, views=[polls])

        session.add(p)

        for item in p.__dict__.items():
            print(item)

        session.commit()


def process_ideas():
    results = query_posts_by_category('ideas')

    for r in results:
        print(r.url)

        html = scrapy.Selector(text=r.body)

        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        session = sessionmaker(bind=engine)()

        title = html.xpath('//div[@class="jam-item-name"]/text()').extract()
        author = html.xpath('//span[@class="jam-item-creator"]/a/text()').extract()
        recency = html.xpath('//span[@class="jam-item-last-updated"]/span[@class="time"]/@timestamp').extract()
        tags = html.xpath('//div[@class="tags"]/div/a/text()').extract()
        content = html.xpath('//div[@class="wiki_content"]').extract()

        # shares

        post_comments = html.xpath('//div[@id="feed-list-container"]//'
                                   'div[@class="feed-action-container"]/span/a/text()').extract()
        feeds_comments = html.xpath('//div[@id="feed-list-container"]//'
                                    'span[@class="feed-comments-count-container feed-meta"]/@data-count').extract()

        # rates

        post_likes = html.xpath('//td[@class="metadata_label content-like-total"]/'
                                'following-sibling::td[@class="metadata_value"]/a/span/text()').extract()
        feeds_likes = html.xpath('//code[@class="feed-likes"]/@data-count').extract()

        views = html.xpath('//td[@class="metadata_label content-views"]/'
                           'following-sibling::td[@class="metadata_value"]/span/text()').extract()

        p = init_post(url=r.baseurl, category='ideas', keyword=KEYWORD, title=title, author=author, recency=recency,
                      tags=tags, content=content, comments=count_comments(post_comments, feeds_comments),
                      likes=count_likes(post_likes, feeds_likes), views=views)

        session.add(p)

        for item in p.__dict__.items():
            print(item)

        session.commit()


def process_groups_events():
    results = query_posts_by_category('events')

    for r in results:
        print(r.url)

        html = scrapy.Selector(text=r.body)

        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        session = sessionmaker(bind=engine)()

        title = html.xpath('//div[@id="content_title"]/text()').extract()
        author = html.xpath('//span[@class="jam-item-creator"]/a/text()').extract()
        recency = html.xpath('//span[@class="jam-item-last-updated"]/span[@class="time"]/@timestamp').extract()
        tags = html.xpath(
            '//div[@class="section event-tags"]//li[@class="token-input-token-tasks event-tag-label"]/text()').extract()
        content = html.xpath('//div[@class="content"]').extract()

        # shares

        post_comments = html.xpath('//span[@class="sap-icon icon-comment"]/span/text()').extract()
        feeds_comments = html.xpath('//div[@id="feed-list-container"]//'
                                    'span[@class="feed-comments-count-container feed-meta"]/@data-count').extract()

        # rates

        post_likes = html.xpath(
            '//span[@class="jam-item-likes"]//a[@class="metadata_value jam-clickable"]/@data-count').extract()
        feeds_likes = html.xpath('//code[@class="feed-likes"]/@data-count').extract()

        views = html.xpath('//span[@class="jam-item-views"]//a[@class="metadata_value "]/@data-count').extract()

        tags_clean = []
        if tags:
            for tag in tags:
                tags_clean.append(tag.strip()[:-2])

        p = init_post(url=r.baseurl, category='events', keyword=KEYWORD, title=title, author=author, recency=recency,
                      tags=tags_clean, content=content, comments=count_comments(post_comments, feeds_comments),
                      likes=count_likes(post_likes, feeds_likes), views=views)

        session.add(p)

        for item in p.__dict__.items():
            print(item)

        session.commit()


def process_groups_documents():
    results = query_posts_by_category('documents')

    for r in results:
        # if 'deleted' in r.url:
        #     continue
        #
        # if 'https://jam4.sapjam.com/groups/ASPWHl2eS9sxTDDlPEj2ma/documents/5elZs949otQPFloq9F8bgh/detail' in r.url:
        #     continue

        print(r.url)

        html = scrapy.Selector(text=r.body)

        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        session = sessionmaker(bind=engine)()

        title = html.xpath('//div[@id="content_title"]/text()').extract()
        author = html.xpath('//span[@class="jam-item-creator"]/a/text()').extract()
        recency = html.xpath('//span[@class="jam-item-last-updated"]/span[@class="time"]/@timestamp').extract()
        tags = html.xpath(
            '//div[@class="content-meta-container jam-flex wrap"]//span[@class="tag-token"]/a/@title').extract()
        content = html.xpath('//div[@id="siv-item-container"]').extract()

        # shares

        post_comments = html.xpath('//span[@class="sap-icon icon-comment"]/span/text()').extract()
        feeds_comments = html.xpath('//div[@id="feed-list-container"]//'
                                    'span[@class="feed-comments-count-container feed-meta"]/@data-count').extract()

        # rates

        post_likes = html.xpath(
            '//span[@class="jam-item-likes"]//a[@class="metadata_value jam-clickable"]/@data-count').extract()
        feeds_likes = html.xpath('//code[@class="feed-likes"]/@data-count').extract()

        views = html.xpath('//span[@class="jam-item-views"]//a[@class="metadata_value "]/@data-count').extract()

        p = init_post(url=r.baseurl, category='documents', keyword=KEYWORD, title=title, author=author, recency=recency,
                      tags=tags, content=content, comments=count_comments(post_comments, feeds_comments),
                      likes=count_likes(post_likes, feeds_likes), views=views)

        session.add(p)

        for item in p.__dict__.items():
            print(item)

        session.commit()


def process_groups_sw_items():
    results = query_posts_by_category('sw_items')

    for r in results:
        print(r.url)

        html = scrapy.Selector(text=r.body)

        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
        session = sessionmaker(bind=engine)()

        title = html.xpath('//div[@id="content_title"]/text()').extract()
        author = html.xpath('//span[@class="jam-item-creator"]/a/text()').extract()
        recency = html.xpath('//span[@class="jam-item-last-updated"]/span[@class="time"]/@timestamp').extract()
        tags = html.xpath(
            '//div[@class="content-meta-container jam-flex wrap"]//span[@class="tag-token"]/a/@title').extract()
        content = html.xpath('//div[@id="sw_item_container"]').extract()

        # shares

        post_comments = html.xpath('//span[@class="sap-icon icon-comment"]/span/text()').extract()
        feeds_comments = html.xpath('//div[@id="feed-list-container"]//'
                                    'span[@class="feed-comments-count-container feed-meta"]/@data-count').extract()

        # rates

        post_likes = html.xpath(
            '//span[@class="jam-item-likes"]//a[@class="metadata_value jam-clickable"]/@data-count').extract()
        feeds_likes = html.xpath('//code[@class="feed-likes"]/@data-count').extract()

        views = html.xpath('//span[@class="jam-item-views"]//a[@class="metadata_value "]/@data-count').extract()

        p = init_post(url=r.baseurl, category='items', keyword=KEYWORD, title=title, author=author, recency=recency,
                      tags=tags, content=content, comments=count_comments(post_comments, feeds_comments),
                      likes=count_likes(post_likes, feeds_likes), views=views)

        session.add(p)

        for item in p.__dict__.items():
            print(item)

        session.commit()


if __name__ == '__main__':
    process_questions()
    process_blogs()
    process_discussions()
    process_wiki()
    process_poll()
    process_ideas()
    process_groups_events()
    process_groups_documents()
    process_groups_sw_items()

    print("All Done")
