import json
import ast
import datetime
import config
import time
import pandas as pd

from sqlalchemy import text
from utils import month_get, day_get
from entity import DomainDataSet, CommunityStructure, PeopleEngagement


def generate_people_cache():
    sql = f'''select username, displaynameformatted as displayname, gender, avatar, profileurl, boardarea, functionalarea, 
            costcenter, officelocation, localinfo, email, mobile, managers, reports
            from people_profile where username in (select distinct jam_post.username from jam_post)'''

    people = config.ENGINE.execute(sql).fetchall()
    print('build cache of people:', len(people))

    results = []

    for p in people:
        if p.username:
            node = dict()
            node["username"] = p.username
            node["displayname"] = p.displayname
            node["gender"] = p.gender
            node["avatar"] = p.avatar
            node["profileurl"] = p.profileurl
            node["boardarea"] = p.boardarea
            node["functionalarea"] = p.functionalarea
            node["costcenter"] = p.costcenter
            node["officelocation"] = p.officelocation
            node["localinfo"] = p.localinfo
            node["email"] = p.email
            node["mobile"] = p.mobile
            node["managers"] = p.managers
            node["reports"] = p.reports

            results.append(node)

    with open(config.CACHE_PROFILES_PATH, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, ensure_ascii=False)


def get_spider_fetch_count(domain):
    request_urls = []
    results = config.ENGINE.execute(f"select topics from spider_jam_search where body <> '[]' and keyword = '{domain}'")
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
    results = config.ENGINE.execute(f"select distinct baseurl from spider_jam_post where keyword = '{domain}'")

    for r in results:
        set_exist_urls_spider.add(
            r.baseurl.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', ''))

    # 获取已处理的urls
    set_exist_urls_processed = set()
    results = config.ENGINE.execute(f"select distinct url from jam_post where keyword = '{domain}'")

    for r in results:
        set_exist_urls_processed.add(r.url.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', ''))

    request_urls = list(set_request_urls - set_exist_urls_spider - set_exist_urls_processed)

    # 最终需要爬取的URL
    print('exist(spider) + exist(processed) + require', len(set_exist_urls_spider), len(set_exist_urls_processed),
          len(request_urls))

    return len(request_urls)


def get_meta_data(domain):
    meta_data = dict()
    print(domain)

    sql = "select count(*) from spider_jam_search where keyword = :domain"
    spider_search_pages = config.ENGINE.execute(text(sql), domain=domain).fetchall()[0][0]
    meta_data['spider_search_pages'] = int(spider_search_pages)
    print('spider_search_pages:', spider_search_pages)

    sql = "select count(*) from spider_jam_post where keyword = :domain"
    spider_posts = config.ENGINE.execute(text(sql), domain=domain).fetchall()[0][0]
    spider_fetch_posts = get_spider_fetch_count(domain)
    meta_data['spider_posts'] = int(spider_posts)
    meta_data['spider_fetch_posts'] = int(spider_fetch_posts)
    print('spider_posts:', spider_posts, 'spider_fetch_posts', spider_fetch_posts)

    sql = "select count(distinct url) from jam_post where keyword = :domain"
    jam_posts = config.ENGINE.execute(text(sql), domain=domain).fetchall()[0][0]
    meta_data['jam_posts'] = int(jam_posts)
    print('jam_posts:', jam_posts)

    sql = '''select post.recency from jam_people_from_post people inner join jam_post post on people.postid = post.id 
             where people.keyword = :domain and post.keyword= :domain and post.recency is not null 
             order by post.recency desc limit 1'''
    result = config.ENGINE.execute(text(sql), domain=domain).fetchall()
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

    sql = '''select post.recency from jam_people_from_post people inner join jam_post post on people.postid = post.id 
             where people.keyword = :domain and post.keyword= :domain and post.recency is not null 
             order by post.recency limit 1'''
    result = config.ENGINE.execute(text(sql), domain=domain).fetchall()
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
    people_creators = config.ENGINE.execute(text(sql), domain=domain).fetchall()[0][0]
    meta_data['people_creators'] = people_creators
    print('people_creators:', people_creators)

    sql = "select count(distinct username) from jam_people_from_post where keyword = :domain and roletype = 'participator'"
    people_participators = config.ENGINE.execute(text(sql), domain=domain).fetchall()[0][0]
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

    if domain_meta and domain_meta["jam_posts_end_recency"]:
        return int(domain_meta["jam_posts_end_recency"])
    else:
        return None


def get_datetime_by_domain(domain):
    with open(config.CACHE_META_DATA) as json_file:
        cache_meta_data = json.load(json_file)

    domain_meta = cache_meta_data[domain]

    if domain_meta:
        return str(domain_meta["jam_posts_start_date"]), str(domain_meta["jam_posts_end_date"])
    else:
        return None, None


def generate_all_cache():
    for domain in config.DOMAINS:
        print(f"generating cache of {domain}")
        counts_list = []
        last_timespot = get_last_timespot_by_domain(domain)
        start_date, end_date = get_datetime_by_domain(domain)

        if start_date is not None and end_date is not None and last_timespot is not None:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

            print(last_timespot)
            nodes_count, links_count, posts_count = generate_cache(domain, last_timespot)
            counts_list.append({"month": datetime.datetime.fromtimestamp(int(last_timespot)).strftime('%Y-%m'),
                                "nodes": int(nodes_count),
                                "links": int(links_count),
                                "posts": int(posts_count)})

            end_date_first_day = datetime.datetime(end_date.year, end_date.month, 1)
            date = end_date_first_day
            while date >= start_date:
                timespot = int(time.mktime(time.strptime(date.strftime("%Y-%m-%d"), '%Y-%m-%d')))

                print(date.strftime("%Y-%m-%d"), timespot)
                nodes_count, links_count, posts_count = generate_cache(domain, timespot)

                date = month_get(date)  # 上个月
                counts_list[-1]['posts'] -= posts_count # 去除累计数，只记录增量
                counts_list.append(
                    {"month": date.strftime("%Y-%m"),
                     "nodes": int(nodes_count),
                     "links": int(links_count),
                     "posts": int(posts_count)})
                print(counts_list[-1])

                df = pd.DataFrame(counts_list)
                df = df.set_index("month")
                df.to_csv("./cache/dataset-{}-statistic.csv".format(domain), encoding='utf-8')


def generate_cache(domain, timespot):
    # Domain Dataset Generate
    ds = DomainDataSet(domain, timespot)

    ds.set_profiles()

    if len(ds.profiles) == 0:
        return 0, 0, 0

    ds.set_contributions()

    if len(ds.contributions) == 0:
        return 0, 0, 0

    ds.set_links()
    ds.social_analysis()
    ds.set_nodes()
    ds.export_dataset()

    # Community Structure
    ds = CommunityStructure(domain, timespot)
    ds.set_nodes_with_links()
    ds.community_analysis()
    ds.set_node_community_attr()

    final_result = ds.export_dataset()

    posts_count = 0

    if len(ds.nodes) > 0:
        for node in ds.nodes:
            posts_count += int(node["posts"])

    print("nodes", len(final_result["nodes"]), "links", len(final_result["links"]))

    return len(final_result["nodes"]), len(final_result["links"]), posts_count


def generate_all_people_engagement(daily=False, filter_people=False):
    for domain in config.DOMAINS:
        print(f"generating people engagement of {domain}")
        counts_list = []
        last_timespot = get_last_timespot_by_domain(domain)
        start_date, end_date = get_datetime_by_domain(domain)

        if start_date is not None and end_date is not None and last_timespot is not None:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

            if daily:
                # print("day", datetime.datetime.fromtimestamp(int(last_timespot)).strftime('%Y-%m-%d'))
                date = end_date
            else:
                # print("month", datetime.datetime.fromtimestamp(int(last_timespot)).strftime('%Y-%m'))
                end_date_first_day = datetime.datetime(end_date.year, end_date.month, 1)
                date = end_date_first_day

            while date >= start_date:
                timespot = int(time.mktime(time.strptime(date.strftime("%Y-%m-%d"), '%Y-%m-%d')))

                print(date.strftime("%Y-%m-%d"), timespot, daily)
                pe_score = generate_people_engagement(domain, timespot, daily, filter_people)

                # 由于作为end_date传入函数，故日期索引需要使用前一天（月）
                if daily:
                    date = day_get(date) # 前一天
                    print("day", date)
                    pe_score['date'] = date.strftime("%Y-%m-%d")

                else:
                    date = month_get(date)  # 上个月
                    print("month", date)
                    pe_score['date'] = date.strftime("%Y-%m")

                print(pe_score)

                counts_list.append(pe_score)

                df = pd.DataFrame(counts_list)
                df = df.set_index("date")

                if filter_people:
                    df.to_csv("./cache/dataset-{}-pe-filter.csv".format(domain), encoding='utf-8')
                else:
                    if daily:
                        df.to_csv("./cache/dataset-{}-pe-daily.csv".format(domain), encoding='utf-8')
                    else:
                        df.to_csv("./cache/dataset-{}-pe.csv".format(domain), encoding='utf-8')


def generate_people_engagement(domain, timespot, daily=False, filter_people=False):
    # Domain People Engagement Score Generate
    ds = PeopleEngagement(domain, timespot, daily, filter_people)

    ds.set_profiles()

    if len(ds.profiles) == 0:
        return ds.people_engagement_score

    ds.set_contributions()

    if len(ds.contributions) == 0:
        return ds.people_engagement_score

    ds.set_links()

    return ds.people_engagement_score


if __name__ == '__main__':
    generate_people_cache()
    generate_meta_data()

    #print(generate_people_engagement('intelligent+enterprise', 1541192623, daily=False, filter_people=True))
    generate_all_people_engagement(filter_people=True)
    #generate_all_people_engagement()

    #generate_all_cache()

    print("done")
