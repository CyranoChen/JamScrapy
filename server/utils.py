import json
import config
import datetime


def max_min_normalize(x):
    x = (x - x.min()) / (x.max() - x.min());
    return x;


def build_profile_dict(profiles):
    profile_dict = dict()

    for p in profiles:
        if p["profileurl"]:
            url = p["profileurl"].split('/')[-1]
            profile_dict[url] = p["username"].strip()
        else:
            print(p)

    return profile_dict


def get_people_username(url):
    url = url.split('/')[-1]

    if len(config.DICT_PROFILES) > 0 and url in config.DICT_PROFILES.keys():
        return config.DICT_PROFILES[url]
    else:
        return ''


def generate_relation(filters, str_relations, black_list=[], source=None, target=None,
                      role=None, ban=False, max_relations=99):
    relations = []
    if str_relations:
        json_list = json.loads(str_relations)
        if not ban or ban and (len(json_list) <= max_relations):
            for item in json_list:
                # url = item['url']
                # name = get_people_username(url)
                name = item['username'].upper()
                if (name in filters) and (name not in black_list) and name != '':
                    if source is not None:
                        relations.append({"source": source.upper(), "target": name, "role": role})
                    elif target is not None:
                        relations.append({"source": name, "target": target.upper(), "role": role})
    return relations


def generate_profiles(usernames, cache_profiles):
    profiles = []

    if len(usernames) > 0:
        filters = [item.username for item in usernames]

        for p in cache_profiles:
            if p["username"] in filters:
                profiles.append(p)

        config.DICT_PROFILES = build_profile_dict(profiles)

    return profiles


def filter_profiles(usernames, filter_list):
    profiles = []

    if len(usernames) > 0 and len(filter_list) > 0:
        dict_filter_list = dict((x, 1) for x in filter_list)
        for p in usernames:
            if p['username'] in dict_filter_list:
                profiles.append(p)
    else:
        profiles = usernames

    return profiles


def get_people_network_type(item, threshold):
    # print(item, item.betweenness)
    if 0 < threshold["betweenness"] <= float(item.betweenness) and 0 < threshold["closeness"] <= float(item.closeness):
        return 'Brokers'
    elif 0 < threshold["closeness"] <= float(item.closeness) and 0 < threshold["degree"] <= float(item.degree):
        return 'Influencers'
    elif 0 < threshold["degree"] <= float(item.degree):
        return 'Connectors'
    else:
        return 'Soloists'

    return 'Soloists'


def day_get(d):
    oneday = datetime.timedelta(days=1)
    day = d - oneday
    date_from = datetime.datetime(day.year, day.month, day.day, 0, 0, 0)
    date_to = datetime.datetime(day.year, day.month, day.day, 23, 59, 59)
    # print('---'.join([str(date_from), str(date_to)]))

    return date_from


def week_get(d):
    dayscount = datetime.timedelta(days=d.isoweekday())
    dayto = d - dayscount
    sixdays = datetime.timedelta(days=6)
    dayfrom = dayto - sixdays
    date_from = datetime.datetime(dayfrom.year, dayfrom.month, dayfrom.day, 0, 0, 0)
    date_to = datetime.datetime(dayto.year, dayto.month, dayto.day, 23, 59, 59)
    # print('---'.join([str(date_from), str(date_to)]))

    return date_from


def month_get(d):
    dayscount = datetime.timedelta(days=d.day)
    dayto = d - dayscount
    date_from = datetime.datetime(dayto.year, dayto.month, 1, 0, 0, 0)
    date_to = datetime.datetime(dayto.year, dayto.month, dayto.day, 23, 59, 59)
    # print('---'.join([str(date_from), str(date_to)]))

    return date_from
