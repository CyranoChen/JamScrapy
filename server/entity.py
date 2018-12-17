import os
import json
import time
import datetime
import numpy as np
from pandas import DataFrame, merge

import community
import networkx as nx

import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt

import config
from tqdm import tqdm
from utils import max_min_normalize, generate_relation, generate_profiles, filter_profiles, get_people_network_type, \
    month_get, day_get


class PeopleNetwork:
    def __init__(self, username, level, s_level, f_level, follow=False):
        self.profiles = dict()
        self.contributions = DataFrame()
        self.links = []
        self.nodes = []
        self.thresholds = {"degree": 5, "closeness": 5, "betweenness": 20}
        self.level = level
        self.s_level = s_level
        self.f_level = f_level
        self.username = username.upper()
        self.follow = follow

    def set_links(self):
        with open(config.CACHE_RELATIONSHIP_PATH) as json_file:
            cache_relationship = json.load(json_file)

        current_lv = 0
        current_gen = {self.username: int(self.level)}  # 设置初始节点为最高层，层数为总层数，之后逐层递减
        self.profiles[f'lv{current_lv}'] = [self.username]  # 生成的树的各层节点集合
        set_nodes = set([self.username])  # 最终生成的节点索引集合，不重复

        relations = []
        while current_lv < self.level:
            print('level:', current_lv)
            print('current:', len(current_gen))

            children = set()
            for r in tqdm(cache_relationship):
                if (not self.follow or self.f_level < current_lv) and r['role'] == 'follow':
                    continue  # ignore

                if (self.s_level < current_lv) and r['role'] == 'comment':
                    continue  # ignore

                if r['source'] in current_gen or r['target'] in current_gen:
                    relations.append(r)

                if r['role'] == 'org':  # 通过组织关系生长
                    if r['source'] in current_gen and r['target'] not in current_gen:
                        children.add(r['target'])
                    elif r['source'] not in current_gen and r['target'] in current_gen:
                        children.add(r['source'])

            current_lv += 1
            children -= set_nodes
            current_gen = {c: int(self.level - current_lv) for c in list(children)}  # 新增成员加入下个迭代
            self.profiles[f'lv{current_lv}'] = list(children)
            set_nodes = set_nodes | children  # 合并新增成员到现有节点集合

            print('children:', len(current_gen))
            print('set_nodes:', len(set_nodes))

        # print(self.profiles)
        self.nodes = list(set_nodes)

        # 生成最终输出的links，包含组织关系org，社交关系social with weight，需反映follow元素
        dict_relations_social = dict()  # (weight, c_mode, f_mode)
        for r in tqdm(relations):
            if r['role'] == 'org':
                self.links.append(r)
                continue

            key = f"{r['source']}>>{r['target']}" if r['source'] <= r['target'] else f"{r['target']}>>{r['source']}"
            if r['role'] == 'comment':
                c_mode = 1 if r['source'] <= r['target'] else 0
                if key in dict_relations_social:
                    v = dict_relations_social[key]
                    if c_mode != v[1]:  # 关系方向相反，或为2
                        dict_relations_social[key] = (v[0]+1, 2, v[2])
                    else:
                        dict_relations_social[key] = (v[0]+1, v[1], v[2])
                else:
                    dict_relations_social[key] = (1, c_mode, -1)

            if self.follow and r['role'] == 'follow':
                f_mode = 1 if r['source'] <= r['target'] else 0
                if key in dict_relations_social:
                    v = dict_relations_social[key]
                    if f_mode != v[2]:  # 关系方向相反，或为2
                        dict_relations_social[key] = (v[0], v[1], 2)
                    else:
                        dict_relations_social[key] = v
                else:
                    dict_relations_social[key] = (0, -1, f_mode)

        for k, v in dict_relations_social.items():
            s, t = k.split('>>')
            self.links.append(
                {'source': s, 'target': t, 'role': 'social', 'weight': v[0], 'c_mode': v[1], 'f_mode': v[2]})

        # self.links = [dict(t) for t in set([tuple(r.items()) for r in relations])]

        print('links:', len(self.links), len(relations))

    # Generate Nodes #
    def set_nodes(self):
        sql = f'''select username, displaynameformatted as displayname, gender, avatar, boardarea, functionalarea,
                  costcenter, officelocation, localinfo, profileurl, email, mobile from people_profile'''

        profiles = config.ENGINE.execute(sql).fetchall()

        dict_nodes = {x: True for x in list(self.nodes)}
        profiles_filtered = [x for x in profiles if x.username.upper() in dict_nodes]

        print('build cache of people profiles:', len(profiles_filtered), '/', len(profiles))

        dict_value = dict()
        for k, v in self.profiles.items():
            if len(v) > 0:
                for uid in v:
                    dict_value[uid] = self.level - int(str(k).replace('lv', ''))

        nodes = []
        for p in tqdm(profiles_filtered):
            if p["username"] is None:
                print(p)
                continue

            username = p['username']

            node = dict()
            node['name'] = username
            node['username'] = username
            node['displayname'] = p["displayname"]
            node['gender'] = p["gender"]
            node['avatar'] = p["avatar"]
            node['boardarea'] = p["boardarea"]
            node['functionalarea'] = p["functionalarea"]
            node['costcenter'] = p["costcenter"]
            node['officelocation'] = p["officelocation"]
            node['localinfo'] = p["localinfo"]
            if p["localinfo"] and len(str.split(p["localinfo"], '/')) > 1:
                node['region'] = str.split(p["localinfo"], '/')[0]
                node['city'] = str.split(p["localinfo"], '/')[1]
            else:
                node['region'] = 'None'
                node['city'] = 'None'
            node['profile'] = p["profileurl"]
            node['email'] = p["email"]
            node['mobile'] = p["mobile"]

            node['value'] = dict_value[username]
            # node['posts'] = int(item.posts)
            # node['comments'] = int(item.comments)
            # node['likes'] = int(item.likes)
            # node['views'] = int(item.views)
            #
            # node['degree'] = round(float(item.degree), 2)
            # node['betweenness'] = round(float(item.betweenness), 2)
            # node['closeness'] = round(float(item.closeness), 2)
            #
            # node['networktype'] = get_people_network_type(item, self.thresholds)

            # node['category'] = 'None'

            nodes.append(node)

        # 去掉重复节点
        self.nodes = [dict(t) for t in set([tuple(d.items()) for d in nodes])]

        print("nodes", len(self.nodes))

    # Export DataSet #
    def export_dataset(self):
        result = {"nodes": self.nodes, "links": self.links}

        if self.follow:
            json_file_path = f"./cache/peoplenetwork-{self.username}-l{self.level}-s{self.s_level}-f{self.f_level}.json"
        else:
            json_file_path = f"./cache/peoplenetwork-{self.username}-l{self.level}-s{self.s_level}-f0.json"

        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(result, json_file, ensure_ascii=False)

        return result


class PeopleEngagement:
    def __init__(self, keyword, timestamp, daily=False, filter_people=False):
        self.profiles = []
        self.contributions = DataFrame()
        self.links = []
        self.nodes = []
        self.thresholds = {"degree": 5, "closeness": 5, "betweenness": 20}
        self.keyword = keyword
        self.filter_people = filter_people
        self.people_engagement_score = {'people': 0, 'posts': 0, 'comments': 0, 'likes': 0, 'views': 0,
                                        'relation_org': 0, 'relation_corp': 0}

        self.date = datetime.datetime.fromtimestamp(int(timestamp))

        self.timestamp_end = int(
            time.mktime(time.strptime(self.date.strftime("%Y-%m-%d 00:00:00"), '%Y-%m-%d %H:%M:%S')))
        end_date = datetime.datetime.fromtimestamp(int(self.timestamp_end))
        begin_date = day_get(end_date) if daily else month_get(end_date)

        self.timestamp_begin = int(
            time.mktime(time.strptime(begin_date.strftime("%Y-%m-%d 00:00:00"), '%Y-%m-%d %H:%M:%S')))
        begin_date = datetime.datetime.fromtimestamp(int(self.timestamp_begin))

        print('begin_time:', begin_date, self.timestamp_begin, 'end_time:', end_date, self.timestamp_end)

    # Query Profiles #
    def set_profiles(self, min_posts=0, filter_people=False):
        sql = f'''select distinct username from
            (select p.username, postid from jam_people_from_post as p left outer join jam_post as post on p.postid = post.id
            where p.keyword='{self.keyword}' and p.roletype='Creator' and p.displayname <> 'Alumni' and post.keyword='{self.keyword}' 
            and post.recency < '{self.timestamp_end}' and post.recency >= '{self.timestamp_begin}') as view_people
            group by view_people.username having count(postid) >= {min_posts} and (username is not null or username <> '')    
            '''

        usernames = config.ENGINE.execute(sql).fetchall()
        print('usernames:', len(usernames))

        with open(config.CACHE_PROFILES_PATH) as json_file:
            cache_profiles = json.load(json_file)

        self.profiles = generate_profiles(usernames, cache_profiles)

        if self.filter_people:
            self.profiles = filter_profiles(self.profiles, config.ARIBA_EMPLOYEES)

        print('profiles:', len(self.profiles))
        self.people_engagement_score['people'] = len(self.profiles)

    # Calculate Contributions #
    def set_contributions(self):
        sql = f'''select username, count(id) as posts, sum(ifnull(comments,0)) as comments, 
                  sum(ifnull(likes,0)) as likes, sum(ifnull(views,0)) as views from jam_post 
                  where keyword = '{self.keyword}' and author <> 'Alumni' 
                  and recency < '{self.timestamp_end}' and recency >= '{self.timestamp_begin}' 
                  group by username having (username is not null or username <> '')
                  order by posts desc, comments desc, likes desc, views desc'''

        query = config.ENGINE.execute(sql)
        columns = query.keys()
        results = query.fetchall()
        print('contributions:', len(results))

        if self.filter_people:
            results = filter_profiles(results, config.ARIBA_EMPLOYEES)

        if len(results) > 0:
            df = DataFrame(results)
            df.columns = columns

            df['posts'] = df['posts'].astype('float64')
            df['comments'] = df['comments'].astype('float64')
            df['likes'] = df['likes'].astype('float64')
            df['views'] = df['views'].astype('float64')

            # record the sum of each indicators
            self.people_engagement_score['posts'] = df['posts'].sum()
            self.people_engagement_score['comments'] = df['comments'].sum()
            self.people_engagement_score['likes'] = df['likes'].sum()
            self.people_engagement_score['views'] = df['views'].sum()

            df['posts_trans'] = np.log(df['posts']).replace([np.inf, -np.inf], 0)
            df['comments_trans'] = np.log(df['comments']).replace([np.inf, -np.inf], 0)
            df['likes_trans'] = np.log(df['likes']).replace([np.inf, -np.inf], 0)
            df['views_trans'] = np.log(df['views']).replace([np.inf, -np.inf], 0)

            df['contribution'] = 0
            weights = {'posts': 12.0, 'comments': 8.0, 'likes': 4.0, 'views': 2.0}
            for key in df.columns:
                if key in weights:
                    df['contribution'] += df[key + '_trans'] * weights[key]

            # 10个人以上才执行变量变换操作
            if len(df) >= 10:
                contribution = df['contribution']
                contribution_perc = max_min_normalize(contribution) * 100
                contribution_perc = np.sqrt(contribution_perc) * 10.0
                contribution_perc[contribution_perc > 100] = 100

                df['contribution'] = contribution_perc

            self.contributions = df.sort_values(['contribution'], ascending=[False])

    # Generate Links #
    def set_links(self, follow=False, max_relations=99):
        filters = dict((p['username'], 1) for p in self.profiles)

        relations = []
        for p in self.profiles:
            relations.extend(generate_relation(filters, p["managers"], config.RELA_BLACK_LIST, target=p["username"],
                                               role='managers'))
            relations.extend(generate_relation(filters, p["reports"], config.RELA_BLACK_LIST, source=p["username"],
                                               role='reports'))
            if follow:
                relations.extend(
                    generate_relation(filters, p["followers"], config.RELA_BLACK_LIST, target=p["username"],
                                      role='followers',
                                      ban=True, max_relations=max_relations))
                relations.extend(
                    generate_relation(filters, p["following"], config.RELA_BLACK_LIST, source=p["username"],
                                      role='following',
                                      ban=True, max_relations=max_relations))

        print('relations:', len(relations))
        self.people_engagement_score['relation_org'] = len(relations)

        sql = f'''select creators.username as target, commenters.username as source from
  (select postid, username from jam_people_from_post
 where keyword = '{self.keyword}' and roletype = 'participator' and position >= 0 and (username is not null or username <> '')
  ) AS commenters
inner join
  (select postid, username from jam_people_from_post
 where keyword = '{self.keyword}' and roletype = 'creator' and position = 0 and (username is not null or username <> '')
  ) AS creators ON commenters.postid = creators.postid
  inner join jam_post as post on commenters.postid = post.id and creators.postid = post.id
where post.recency < '{self.timestamp_end}' and post.recency >= '{self.timestamp_begin}' 
                    '''

        comments = config.ENGINE.execute(sql).fetchall()

        print("comments:", len(comments))

        self.people_engagement_score['relation_corp'] = 0
        if len(comments) > 0:
            for c in comments:
                if c.source in filters and c.target in filters:
                    relations.append({"source": c.source, "target": c.target, "role": 'comment'})
                    self.people_engagement_score['relation_corp'] += 1

        print('relations with comments:', len(relations))

        # 合并对应所有role关系，设置不同权重
        relations_dict = dict()

        for r in relations:
            key_s = f"{r['source']}>{r['target']}"
            key_t = f"{r['target']}>{r['source']}"
            if key_s in relations_dict.keys():
                relations_dict[key_s].append(r)
            elif key_t in relations_dict.keys():
                relations_dict[key_t].append(r)
            else:
                relations_dict[key_s] = [r]

        print('relations without duplicated:', len(relations_dict))

        links = []

        for k, v in relations_dict.items():
            # 初始化关系权重
            weight = 0
            source = v[0]['source']
            target = v[0]['target']

            for r in v:
                if r['role'] == 'comment':
                    weight += 20
                elif r['role'] == 'managers' or r['role'] == 'reports':
                    weight += 5
                elif r['role'] == 'followers' or r['role'] == 'following':
                    weight += 2

            links.append({"source": source, "target": target, "weight": float(weight)})

        # transfer weight value of link
        for l in links:
            l['weight'] = np.sqrt(l['weight']) * 10.0

        self.links = links

        print("links:", len(self.links))


class CommunityStructure:
    def __init__(self, keyword, timestamp, nonorg=False):
        self.nodes = []
        self.links = []
        self.graph = nx.Graph(name='community-network')
        self.partition = []
        self.community_size = dict()
        self.keyword = keyword
        self.timestamp = timestamp
        self.nonorg = nonorg
        if nonorg:
            self.source_file_path = f"./cache/dataset-{keyword.lower()}-{str(timestamp)}-nonorg.json"
        else:
            self.source_file_path = f"./cache/dataset-{keyword.lower()}-{str(timestamp)}.json"

    def set_nodes_with_links(self):
        if not os.path.exists(self.source_file_path):
            return

        with open(self.source_file_path) as json_file:
            ds = json.load(json_file)
            self.nodes = ds['nodes']
            self.links = ds['links']

        print('nodes:', len(self.nodes), 'links:', len(self.links))

    def community_analysis(self):
        if len(self.nodes) == 0 or len(self.links) == 0:
            return

        # g = nx.Graph(name='community-network')
        for item in self.links:
            self.graph.add_edge(item['source'], item['target'])

        self.partition = community.best_partition(self.graph)

        print('partition:', len(self.partition))

        if len(self.partition) > 0:
            for k, v in self.partition.items():
                # v -> ###### string
                str_v = str(v).zfill(6)
                if str_v in self.community_size:
                    self.community_size[str_v] += 1
                else:
                    self.community_size[str_v] = 1

        print('community:', len(self.community_size))

    def set_node_community_attr(self):
        if len(self.nodes) == 0 or len(self.links) == 0 or len(self.partition) == 0:
            return

        for node in self.nodes:
            if node['name'] in self.partition:
                node['community'] = str(self.partition[node['name']]).zfill(6)
                node['community_size'] = self.community_size[node['community']]

    def export_dataset(self):
        result = {"nodes": self.nodes, "links": self.links}
        if self.nonorg:
            json_file_path = f"./cache/dataset-{self.keyword.lower()}-{str(self.timestamp)}-nonorg.json"
        else:
            json_file_path = f"./cache/dataset-{self.keyword.lower()}-{str(self.timestamp)}.json"
        with open(json_file_path, 'w',
                  encoding='utf-8') as json_file:
            json.dump(result, json_file, ensure_ascii=False)

        return result


class DomainDataSet:
    def __init__(self, keyword, timestamp, nonorg=False):
        self.profiles = []
        self.contributions = DataFrame()
        self.links = []
        self.nodes = []
        self.thresholds = {"degree": 5, "closeness": 5, "betweenness": 20}
        self.keyword = keyword
        self.timestamp = timestamp
        self.nonorg = nonorg

    # Query Profiles #
    def set_profiles(self, min_posts=0):
        sql = f'''select distinct username from
            (select p.username, postid from jam_people_from_post as p left outer join jam_post as post on p.postid = post.id
            where p.keyword='{self.keyword}' and p.roletype='Creator' and p.displayname <> 'Alumni'
            and post.keyword='{self.keyword}' and post.recency <= '{self.timestamp}') as view_people
            group by view_people.username having count(postid) >= {min_posts} and (username is not null or username <> '')    
            '''

        usernames = config.ENGINE.execute(sql).fetchall()
        print('usernames:', len(usernames))

        with open(config.CACHE_PROFILES_PATH) as json_file:
            cache_profiles = json.load(json_file)

        self.profiles = generate_profiles(usernames, cache_profiles)
        print('profiles:', len(self.profiles))

    # Calculate Contributions #
    def set_contributions(self):
        sql = f'''select username, count(id) as posts, sum(ifnull(comments,0)) as comments, 
                  sum(ifnull(likes,0)) as likes, sum(ifnull(views,0)) as views from jam_post 
                  where keyword = '{self.keyword}' and author <> 'Alumni' and recency <= '{self.timestamp}' 
                  group by username having (username is not null or username <> '')
                  order by posts desc, comments desc, likes desc, views desc'''

        query = config.ENGINE.execute(sql)
        print('contributions:', query.rowcount)

        if query.rowcount > 0:
            df = DataFrame(query.fetchall())
            df.columns = query.keys()

            df['posts'] = df['posts'].astype('float64')
            df['comments'] = df['comments'].astype('float64')
            df['likes'] = df['likes'].astype('float64')
            df['views'] = df['views'].astype('float64')

            df['posts_trans'] = np.log(df['posts']).replace([np.inf, -np.inf], 0)
            df['comments_trans'] = np.log(df['comments']).replace([np.inf, -np.inf], 0)
            df['likes_trans'] = np.log(df['likes']).replace([np.inf, -np.inf], 0)
            df['views_trans'] = np.log(df['views']).replace([np.inf, -np.inf], 0)

            df['contribution'] = 0
            weights = {'posts': 12.0, 'comments': 8.0, 'likes': 4.0, 'views': 2.0}
            for key in df.columns:
                if key in weights:
                    df['contribution'] += df[key + '_trans'] * weights[key]

            # 10个人以上才执行变量变换操作
            if len(df) >= 10:
                contribution = df['contribution']
                contribution_perc = max_min_normalize(contribution) * 100
                contribution_perc = np.sqrt(contribution_perc) * 10.0
                contribution_perc[contribution_perc > 100] = 100

                df['contribution'] = contribution_perc

            self.contributions = df.sort_values(['contribution'], ascending=[False])
            # self.contributions.describe(exclude=[np.object]).astype(np.int64).T

    # Generate Links #
    def set_links(self, follow=False, max_relations=99):
        filters = dict((p['username'], 1) for p in self.profiles)

        relations = []
        for p in self.profiles:
            if not self.nonorg:
                relations.extend(generate_relation(filters, p["managers"], config.RELA_BLACK_LIST, target=p["username"],
                                                   role='managers', ))
                relations.extend(generate_relation(filters, p["reports"], config.RELA_BLACK_LIST, source=p["username"],
                                                   role='reports'))
            if follow:
                relations.extend(
                    generate_relation(relations, filters, p["followers"], config.RELA_BLACK_LIST, target=p["username"],
                                      role='followers',
                                      ban=True, max_relations=max_relations))
                relations.extend(
                    generate_relation(relations, filters, p["following"], config.RELA_BLACK_LIST, source=p["username"],
                                      role='following',
                                      ban=True, max_relations=max_relations))

        print('relations:', len(relations))

        sql = f'''select creators.username as target, commenters.username as source from
  (select postid, username from jam_people_from_post
 where keyword = '{self.keyword}' and roletype = 'participator' and position >= 0 and (username is not null or username <> '')
  ) AS commenters
inner join
  (select postid, username from jam_people_from_post
 where keyword = '{self.keyword}' and roletype = 'creator' and position = 0 and (username is not null or username <> '')
  ) AS creators ON commenters.postid = creators.postid
  inner join jam_post as post on commenters.postid = post.id and creators.postid = post.id
where post.recency <= '{self.timestamp}'
                    '''

        comments = config.ENGINE.execute(sql).fetchall()

        print("comments:", len(comments))

        for c in comments:
            if c.source in filters and c.target in filters:
                relations.append({"source": c.source, "target": c.target, "role": 'comment'})

        print('relations with comments:', len(relations))

        # 合并对应所有role关系，设置不同权重
        relations_dict = dict()

        for r in relations:
            key_s = f"{r['source']}>{r['target']}"
            key_t = f"{r['target']}>{r['source']}"
            if key_s in relations_dict.keys():
                relations_dict[key_s].append(r)
            elif key_t in relations_dict.keys():
                relations_dict[key_t].append(r)
            else:
                relations_dict[key_s] = [r]

        print('relations without duplicated:', len(relations_dict))

        links = []

        for k, v in relations_dict.items():
            # 初始化关系权重
            weight = 0
            source = v[0]['source']
            target = v[0]['target']

            for r in v:
                if r['role'] == 'comment':
                    weight += 20
                elif r['role'] == 'managers' or r['role'] == 'reports':
                    weight += 5
                elif r['role'] == 'followers' or r['role'] == 'following':
                    weight += 2

            links.append({"source": source, "target": target, "weight": float(weight)})

        # transfer weight value of link
        for l in links:
            l['weight'] = np.sqrt(l['weight']) * 10.0

        self.links = links

        print("links:", len(self.links))

    # Analyze Social Network #
    def social_analysis(self):
        if len(self.links) > 0:
            g = nx.Graph(name='social-network')
            for item in self.links:
                g.add_edge(item['source'], item['target'])

            degree = nx.degree_centrality(g)
            closeness = nx.closeness_centrality(g)
            betweenness = nx.betweenness_centrality(g)

            print('social graph nodes:', len(g.nodes))

            nx_list = []
            num_nodes = len(g.nodes)

            for name in g.nodes:
                node = dict()
                node['username'] = name
                node['degree'] = degree[name] * num_nodes
                node['closeness'] = closeness[name] * num_nodes
                node['betweenness'] = betweenness[name] * num_nodes
                nx_list.append(node)

            df_links = DataFrame(nx_list)
            df = self.contributions
            df = merge(df, df_links, on='username', how='left')
            df = df.where(df.notnull(), 0)
            self.contributions = df

            box = plt.boxplot(df['closeness'][df['closeness'] > 0])
            closeness_min = box['whiskers'][0].get_ydata().min()
            closeness_max = box['whiskers'][1].get_ydata().max()
            closeness = df['closeness'][(df['closeness'] >= closeness_min) & (df['closeness'] <= closeness_max)]
            self.thresholds["closeness"] = max(self.thresholds["closeness"], closeness.max() - 2. * closeness.std())
            print("closeness threshold:", self.thresholds["closeness"])

            betweenness = df['betweenness'][df['betweenness'] > 0]
            box = plt.boxplot(betweenness)
            if box['fliers'][0].get_ydata().any():
                self.thresholds["betweenness"] = max(self.thresholds["betweenness"], box['fliers'][0].get_ydata().min())
            else:
                self.thresholds["betweenness"] = max(self.thresholds["betweenness"],
                                                     box['whiskers'][1].get_ydata().max())
            print("betweenness threshold:", self.thresholds["betweenness"])

            degree = df['degree'][df['degree'] > 0]
            box = plt.boxplot(degree)
            self.thresholds["degree"] = max(self.thresholds["degree"], box['whiskers'][1].get_ydata().max())
            print("degree threshold:", self.thresholds["degree"])
        else:
            df = self.contributions
            df["degree"] = 0
            df["closeness"] = 0
            df["betweenness"] = 0
            self.contributions = df

    # Generate Nodes #
    def set_nodes(self):
        nodes = []
        df = self.contributions

        for p in self.profiles:
            if p["username"] is None:
                print(p)
                continue

            item = df[df['username'] == p["username"]]

            if len(item) > 0:
                node = dict()
                node['name'] = p["username"]
                node['username'] = p["username"]
                node['displayname'] = p["displayname"]
                node['gender'] = p["gender"]
                node['avatar'] = p["avatar"]
                node['boardarea'] = p["boardarea"]
                node['functionalarea'] = p["functionalarea"]
                node['costcenter'] = p["costcenter"]
                node['officelocation'] = p["officelocation"]
                node['localinfo'] = p["localinfo"]
                if p["localinfo"] and len(str.split(p["localinfo"], '/')) > 1:
                    node['region'] = str.split(p["localinfo"], '/')[0]
                    node['city'] = str.split(p["localinfo"], '/')[1]
                else:
                    node['region'] = 'None'
                    node['city'] = 'None'
                node['profile'] = p["profileurl"]
                node['email'] = p["email"]
                node['mobile'] = p["mobile"]

                node['value'] = round(float(item.contribution), 2)
                node['posts'] = int(item.posts)
                node['comments'] = int(item.comments)
                node['likes'] = int(item.likes)
                node['views'] = int(item.views)

                node['degree'] = round(float(item.degree), 2)
                node['betweenness'] = round(float(item.betweenness), 2)
                node['closeness'] = round(float(item.closeness), 2)

                node['networktype'] = get_people_network_type(item, self.thresholds)

                # node['category'] = 'None'

                nodes.append(node)

        # 去掉重复节点
        self.nodes = [dict(t) for t in set([tuple(d.items()) for d in nodes])]

        print("nodes", len(self.nodes))

    # Export DataSet #
    def export_dataset(self):
        result = {"nodes": self.nodes, "links": self.links}
        if self.nonorg:
            json_file_path = f"./cache/dataset-{self.keyword.lower()}-{str(self.timestamp)}-nonorg.json"
        else:
            json_file_path = f"./cache/dataset-{self.keyword.lower()}-{str(self.timestamp)}.json"

        with open(json_file_path, 'w',
                  encoding='utf-8') as json_file:
            json.dump(result, json_file, ensure_ascii=False)

        return result
