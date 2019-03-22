# -*- coding:utf-8 -*-
import ast
import json
import re
import requests
import urllib3
import time
import random

from tqdm import tqdm

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from JamScrapy import config
from JamScrapy.preprocess.entity import Comment

urllib3.disable_warnings()

PROFILES = dict()


def initial_profiles():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

    results = engine.execute(f"select profileurl, username from people_profile")

    for r in results:
        url = r.profileurl.split('/')[-1]
        PROFILES[url] = r.username.strip()

    print('PROFILES DICT:', len(PROFILES))


def get_people_username(profileurl):
    url = profileurl.split('/')[-1]

    if len(PROFILES) > 0 and url in PROFILES:
        return PROFILES[url]
    else:
        return None


def get_total_request_urls():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

    sql = 'select topics from spider_jam_comment order by id'
    results = engine.execute(sql).fetchall()

    print('total search pages', len(results))

    list_request_urls = []
    for r in results:
        list_request_urls.extend(ast.literal_eval(r.topics))
    set_request_urls = set(list_request_urls)

    sql = 'select baseurl from jam_comment'
    results = engine.execute(sql).fetchall()
    set_exist_urls = set([r.baseurl for r in results])

    list_request_urls = list(set_request_urls - set_exist_urls)
    print('set_request_urls - set_exist_urls:', len(set_request_urls), len(set_exist_urls), len(list_request_urls))

    random.shuffle(list_request_urls)

    return list_request_urls


def get_json_from_raw_text(content):
    m = re.search(r"namespace: \'MAIN\',(.*?) payload(.*?) feedItems: (.*?)\"anchor_log_id", content, re.DOTALL)
    if m:
        raw = m.group(3)
        raw1 = raw[0:-1] + '}}'
        raw2 = raw[0:-1] + '}]}}'
        try:
            json_obj = json.loads(raw1)
        except:
            json_obj = json.loads(raw2)
        key = next(iter(json_obj))
        return json_obj[key]
    else:
        print('not match')
        return None


def save_comment(baseurl, url, title, category, author, post_recency, post_metadata,
                 commentor, comment_recency, comment_metadata, subcomment):
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()

    c = Comment(
        baseurl=baseurl,
        url=url,
        title=title,
        category=category,
        author=author,
        postrecency=post_recency,
        postmetadata=post_metadata,
        commentor=commentor,
        commentrecency=comment_recency,
        commentmetadata=comment_metadata,
        subcomment=subcomment
    )

    for attr in dir(c):
        if not attr.startswith('__'):
            print(f"comment.{attr} = {getattr(c, attr)}")

    session.add(c)
    session.commit()
    session.close()
    print('-' * 20, 'saved')


def persist_comments(obj, url):
    count_comments = 0
    count_sub_comments = 0
    if obj is not None and len(obj['comments']) > 0:
        print('html raw json:', obj)
        for c in obj['comments']:
            author = get_people_username(obj['member']['param'])
            commentor = get_people_username(c['member']['param'])
            if 'content_url' in obj['content']:
                content_url = obj['content']['content_url']
            elif 'url' in obj['content']:
                content_url = obj['content']['url']
            else:
                content_url = None
            if author is not None and commentor is not None:
                save_comment(baseurl=url,
                             url=content_url,
                             title=obj['content']['name'] if 'name' in obj['content'] else None,
                             category=obj['type'],
                             author=author,
                             post_recency=obj['createdAt'],
                             post_metadata=str(obj['metadata']),
                             commentor=commentor,
                             comment_recency=c['createdAt'],
                             comment_metadata=str(c['metadata']),
                             subcomment=0)
                count_comments += 1
            else:
                if author is None:
                    print('author not found:', obj['member']['param'], obj['member']['FullName'])

                if commentor is None:
                    print('commentor not found:', c['member']['param'], c['member']['FullName'])

            # save sub comments
            if len(c['comments']) > 0:
                for sub_c in c['comments']:
                    sub_commentor = get_people_username(sub_c['member']['param'])
                    if 'content_url' in obj['content']:
                        content_url = obj['content']['content_url']
                    elif 'url' in obj['content']:
                        content_url = obj['content']['url']
                    else:
                        content_url = None
                    if commentor is not None and sub_commentor is not None:
                        save_comment(baseurl=url,
                                     url=content_url,
                                     title=obj['content']['name'] if 'name' in obj['content'] else None,
                                     category=obj['type'],
                                     author=commentor,
                                     post_recency=c['createdAt'],
                                     post_metadata=str(c['metadata']),
                                     commentor=sub_commentor,
                                     comment_recency=sub_c['createdAt'],
                                     comment_metadata=str(sub_c['metadata']),
                                     subcomment=1)
                    else:
                        print('sub_commentor not found:', sub_c['member']['param'], sub_c['member']['FullName'])
                    count_sub_comments += 1

    print('persist comments:', count_comments, count_sub_comments)


def preprocess_comment(url):
    r = requests.get('https://' + config.DOMAIN + url, cookies=config.JAM_COOKIE, verify=False, timeout=30)
    print(r.url)

    if r.status_code == 200:
        obj = get_json_from_raw_text(r.text)
        if obj is None:
            return

        persist_comments(obj, url)
    else:
        print(r.status_code)


def preprocess_comments():
    list_urls = get_total_request_urls()

    list_processed_urls = dict()
    for url in tqdm(list_urls):
        if url not in list_processed_urls:
            try:
                preprocess_comment(url)
                list_processed_urls[url] = 1
            except:
                continue


if __name__ == '__main__':
    initial_profiles()

    preprocess_comments()

    print("All Done")
