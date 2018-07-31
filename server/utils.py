import json
import config


def max_min_normalize(x):
    x = (x - x.min()) / (x.max() - x.min());
    return x;


def build_profile_dict(profiles):
    profile_dict = dict()

    for p in profiles:
        if p.profileurl:
            url = p.profileurl.split('/')[-1]
            profile_dict[url] = p.username.strip()
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
                url = item['url']
                name = get_people_username(url)
                if (name in filters) and (name not in black_list) and name != '':
                    if source is not None:
                        relations.append({"source": source, "target": name, "role": role})
                    elif target is not None:
                        relations.append({"source": name, "target": target, "role": role})
    return relations


# def get_people_contribution(username):
#     item = df[df['username'] == username]
#     if item.size > 0:
#         return float(item['contribution']);
#     else:
#         return 0;
#
#
# def get_people_indicators(username, key):
#     item = df[df['username'] == username]
#     if item.size > 0 and key in item.keys():
#         return int(item[key])
#     else:
#         return 0;
#
#
# def get_people_network_degree(username):
#     if username in nodes_degree.keys():
#         return int(nodes_degree[username])
#     else:
#         return 0;


def get_people_network_type(item, threshold):
    # print(item, item.betweenness)
    if float(item.betweenness) >= threshold["betweenness"]:
        return 'Brokers'
    elif float(item.closeness) >= threshold["closeness"]:
        return 'Influencers'
    elif float(item.degree) >= threshold["degree"]:
        return 'Connectors'
    else:
        return 'Soloists'

    return 'Soloists'
