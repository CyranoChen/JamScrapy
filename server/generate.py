import json
import ast
import datetime

from sqlalchemy import create_engine, text

import config


def generate_people_cache():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

    sql = f'''select username, displaynameformatted as displayname, avatar, profileurl, boardarea, functionalarea, 
            costcenter, officelocation, localinfo, email, mobile, managers, reports
            from people_profile where username in (select distinct jam_post.username from jam_post)'''

    people = engine.execute(sql).fetchall()
    print('build cache of people:', len(people))

    results = []

    for p in people:
        if p.username:
            node = dict()
            node["username"] = p.username
            node["displayname"] = p.displayname
            node["avatar"] = p.avatar
            node["profileurl"] = p.profileurl
            node["boardarea"] = p.boardarea
            node["functionalarea"] = p.functionalarea
            node["costcenter"] = p.costcenter
            node["officelocation"] = p.officelocation
            node["localinfo"] = p.localinfo
            node["email"] = p.email
            node["mobile"]  = p.mobile
            node["managers"] = p.managers
            node["reports"] = p.reports

            results.append(node)

    with open(config.CACHE_PROFILES_PATH, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, ensure_ascii=False)


def get_spider_fetch_count(domain):
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

    request_urls = []
    results = engine.execute(f"select topics from spider_jam_search where body <> '[]' and keyword = '{domain}'")
    # print('total search pages', results.rowcount)

    for r in results:
        request_urls.extend(ast.literal_eval(r.topics))

    set_request_urls = set()
    for r in request_urls:
        set_request_urls.add(r.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', ''))

    # 全部不重复的URL set
    print('distinct post (processed) url', len(set_request_urls), '/', len(request_urls))

    # 获取未处理的urls
    set_exist_urls_spider = set()
    results = engine.execute(f"select distinct baseurl from spider_jam_post where keyword = '{domain}'")

    for r in results:
        set_exist_urls_spider.add(
            r.baseurl.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', ''))

    # 获取已处理的urls
    set_exist_urls_processed = set()
    results = engine.execute(f"select distinct url from jam_post where keyword = '{domain}'")

    for r in results:
        set_exist_urls_processed.add(r.url.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', ''))

    request_urls = list(set_request_urls - set_exist_urls_spider - set_exist_urls_processed)

    # 最终需要爬取的URL
    print('exist(spider) + exist(processed) + require', len(set_exist_urls_spider), len(set_exist_urls_processed),
          len(request_urls))

    return len(request_urls)


def get_meta_data(domain):
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

    meta_data = dict()
    print(domain)

    sql = "select count(*) from spider_jam_search where keyword = :domain"
    spider_search_pages = engine.execute(text(sql), domain=domain).fetchall()[0][0]
    meta_data['spider_search_pages'] = int(spider_search_pages)
    print('spider_search_pages:', spider_search_pages)

    sql = "select count(*) from spider_jam_post where keyword = :domain"
    spider_posts = engine.execute(text(sql), domain=domain).fetchall()[0][0]
    spider_fetch_posts = get_spider_fetch_count(domain)
    meta_data['spider_posts'] = int(spider_posts)
    meta_data['spider_fetch_posts'] = int(spider_fetch_posts)
    print('spider_posts:', spider_posts, 'spider_fetch_posts', spider_fetch_posts)

    sql = "select count(distinct url) from jam_post where keyword = :domain"
    jam_posts = engine.execute(text(sql), domain=domain).fetchall()[0][0]
    meta_data['jam_posts'] = int(jam_posts)
    print('jam_posts:', jam_posts)

    sql = "select recency from jam_post where keyword = :domain and recency is not null order by recency desc limit 1"
    result = engine.execute(text(sql), domain=domain).fetchall()
    if len(result) > 0:
        recency = result[0][0]
        if recency:
            meta_data['jam_posts_end_date'] = datetime.datetime.fromtimestamp(int(recency) / 1000).strftime('%Y-%m-%d')
            meta_data['jam_posts_end_recency'] = int(int(recency) / 1000)
        else:
            meta_data['jam_posts_end_date'] = None
            meta_data['jam_posts_end_recency'] = None
    else:
        meta_data['jam_posts_end_date'] = None
        meta_data['jam_posts_end_recency'] = None
    print('jam_posts_end_date:', meta_data['jam_posts_end_date'], meta_data['jam_posts_end_recency'])

    sql = "select recency from jam_post where keyword = :domain and recency is not null order by recency limit 1"
    result = engine.execute(text(sql), domain=domain).fetchall()
    if len(result) > 0:
        recency = result[0][0]
        if recency:
            meta_data['jam_posts_start_date'] = datetime.datetime.fromtimestamp(int(recency) / 1000).strftime(
                '%Y-%m-%d')
            meta_data['jam_posts_start_recency'] = int(int(recency) / 1000)
        else:
            meta_data['jam_posts_start_date'] = None
            meta_data['jam_posts_start_recency'] = None
    else:
        meta_data['jam_posts_start_date'] = None
        meta_data['jam_posts_start_recency'] = None
    print('jam_posts_start_date:', meta_data['jam_posts_start_date'], meta_data['jam_posts_start_recency'])

    sql = "select count(distinct username) from jam_people_from_post where keyword = :domain and roletype = 'creator'"
    people_creators = engine.execute(text(sql), domain=domain).fetchall()[0][0]
    meta_data['people_creators'] = people_creators
    print('people_creators:', people_creators)

    sql = "select count(distinct username) from jam_people_from_post where keyword = :domain and roletype = 'participator'"
    people_participators = engine.execute(text(sql), domain=domain).fetchall()[0][0]
    meta_data['people_participators'] = people_participators
    print('people_participators:', people_participators)

    print('\n')

    return meta_data


def generate_meta_data():
    results = dict()
    for d in config.DOMAINS:
        results[d] = get_meta_data(d)

    print(json.dumps(results))

    with open(config.CACHE_META_DATA, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, ensure_ascii=False)


def get_last_timespot_by_domain(domain):
    # engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    #
    # sql = "select recency from jam_post where keyword = :domain and recency is not null order by recency desc limit 1"
    # result = engine.execute(text(sql), domain=domain).fetchall()

    with open(config.CACHE_META_DATA) as json_file:
        cache_meta_data = json.load(json_file)

    domain_meta = cache_meta_data[domain]

    if domain_meta:
        return int(domain_meta["jam_posts_end_recency"])
    else:
        return None


if __name__ == '__main__':
    generate_people_cache()
    generate_meta_data()

    print("done")