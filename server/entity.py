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
from utils import max_min_normalize, generate_relation, generate_profiles, filter_profiles, get_people_network_type, month_get, day_get


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

        self.timestamp_end = int(time.mktime(time.strptime(self.date.strftime("%Y-%m-%d 00:00:00"), '%Y-%m-%d %H:%M:%S')))
        end_date = datetime.datetime.fromtimestamp(int(self.timestamp_end))
        begin_date = day_get(end_date) if daily else month_get(end_date)

        self.timestamp_begin = int(time.mktime(time.strptime(begin_date.strftime("%Y-%m-%d 00:00:00"), '%Y-%m-%d %H:%M:%S')))
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
        filters = [p["username"] for p in self.profiles]

        relations = []
        for p in self.profiles:
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
        self.people_engagement_score['relation_org'] = len(relations)

        sql = f'''select creators.username as source, commenters.username as target from
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
        filters = [p["username"] for p in self.profiles]

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

        sql = f'''select creators.username as source, commenters.username as target from
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
