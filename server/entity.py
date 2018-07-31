import numpy as np
from pandas import DataFrame, merge
from sqlalchemy import create_engine
import networkx as nx
import matplotlib.pyplot as plt
import json

import config
from utils import max_min_normalize, build_profile_dict, generate_relation, get_people_network_type


class DomainDataSet:
    def __init__(self, keyword, timestamp):
        self.profiles = []
        self.contributions = DataFrame()
        self.links = []
        self.nodes = []
        self.thresholds = {"degree": 0, "closeness": 0, "betweenness": 0}
        self.keyword = keyword
        self.timestamp = timestamp

    # Query Profiles #
    def set_profiles(self, min_posts=0):
        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

        sql = f'''select profile.username, profile.displayname, profile.avatar, profile.profileurl,
            profile.boardarea, profile.functionalarea, profile.costcenter, profile.officelocation, profile.localinfo,
            profile.email, profile.mobile, profile.managers, profile.reports from
            (select username from
            (select p.username, postid from jam_people_from_post as p left outer join jam_post as post on p.postid = post.id
            where p.keyword='{self.keyword}' and p.roletype='Creator' and p.displayname <> 'Alumni'
            and post.keyword='{self.keyword}' and post.recency < '{self.timestamp}') as view_people
            group by view_people.username having count(postid) >= {min_posts}) as people
            left outer join people_profile as profile on people.username = profile.username'''

        self.profiles = engine.execute(sql).fetchall()
        print('profiles:', len(self.profiles))

        # load as cache while server starts
        config.DICT_PROFILES = build_profile_dict(self.profiles)

    # Calculate Contributions #
    def set_contributions(self):
        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

        sql = f'''select username, count(id) as posts, sum(ifnull(comments,0)) as comments, 
                  sum(ifnull(likes,0)) as likes, sum(ifnull(likes,0)) as views from jam_post 
                  where keyword = '{self.keyword}' and author <> 'Alumni' and recency < '{self.timestamp}' group by username
                  order by posts desc, comments desc, likes desc, views desc'''

        query = engine.execute(sql)
        print('contributions:', query.rowcount)

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

        contribution = df['contribution']
        contribution_perc = max_min_normalize(contribution) * 100
        contribution_perc = np.sqrt(contribution_perc) * 10.0
        contribution_perc[contribution_perc > 100] = 100

        df['contribution'] = contribution_perc

        self.contributions = df.sort_values(['contribution'], ascending=[False])
        #self.contributions.describe(exclude=[np.object]).astype(np.int64).T

    # Generate Links #
    def set_links(self, follow=False, max_relations=99):
        filters = [p.username for p in self.profiles]

        relations = []
        for p in self.profiles:
            relations.extend(
                generate_relation(filters, p.managers, config.RELA_BLACK_LIST, target=p.username, role='managers', ))
            relations.extend(
                generate_relation(filters, p.reports, config.RELA_BLACK_LIST, source=p.username, role='reports'))
            if follow:
                generate_relation(relations, filters, p.followers, config.RELA_BLACK_LIST, target=p.username,
                                  role='followers',
                                  ban=True, max_relations=max_relations)
                generate_relation(relations, filters, p.following, config.RELA_BLACK_LIST, source=p.username,
                                  role='following',
                                  ban=True, max_relations=max_relations)

        print('relations:', len(relations))

        engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

        sql = f'''select * from (select commenters.postid, commenters.position, creators.username as source, commenters.username as target from
            (select * from jam_people_from_post where keyword = '{self.keyword}' and roletype = 'participator' and position >= 0) AS commenters
            inner join (select * from jam_people_from_post where keyword = '{self.keyword}' and roletype = 'creator' and position = 0) AS creators
            ON commenters.postid = creators.postid ) as t where source <> 'Alumni' or target <> 'Alumni' order by postid, position'''

        comments = engine.execute(sql).fetchall()

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
        self.thresholds["closeness"] = closeness.max() - 1. * closeness.std()
        print("closeness threshold:", self.thresholds["closeness"])

        betweenness = df['betweenness'][df['betweenness'] > 0]
        box = plt.boxplot(betweenness)
        self.thresholds["betweenness"] = box['fliers'][0].get_ydata().min()
        print("betweenness threshold:", self.thresholds["betweenness"])

        degree = df['degree'][df['degree'] > 0]
        box = plt.boxplot(degree)
        self.thresholds["degree"] = box['fliers'][0].get_ydata().min()
        print("degree threshold:", self.thresholds["degree"])

    # Generate Nodes #
    def set_nodes(self):
        nodes = []
        df = self.contributions

        for p in self.profiles:
            if p.username is None:
                print(p)
                continue

            item = df[df['username'] == p.username]

            if len(item) > 0:
                node = dict()
                node['name'] = p.username
                node['username'] = p.username
                node['displayname'] = p.displayname
                node['avatar'] = p.avatar
                node['boardarea'] = p.boardarea
                node['functionalarea'] = p.functionalarea
                node['costcenter'] = p.costcenter
                node['officelocation'] = p.officelocation
                node['localinfo'] = p.localinfo
                if p.localinfo:
                    node['region'] = str.split(p.localinfo, '/')[0]
                    node['city'] = str.split(p.localinfo, '/')[1]
                else:
                    node['region'] = 'None'
                    node['city'] = 'None'
                node['profile'] = p.profileurl
                node['email'] = p.email
                node['mobile'] = p.mobile

                node['value'] = round(float(item.contribution), 2)
                node['posts'] = int(item.posts)
                node['comments'] = int(item.comments)
                node['likes'] = int(item.likes)
                node['views'] = int(item.views)

                node['degree'] = round(float(item.degree), 2)
                node['betweenness'] = round(float(item.betweenness), 2)
                node['closeness'] = round(float(item.closeness), 2)

                node['networktype'] = get_people_network_type(item, self.thresholds)

                nodes.append(node)

        # 去掉重复节点
        self.nodes = [dict(t) for t in set([tuple(d.items()) for d in nodes])]

        print("nodes", len(self.nodes))

    # Export DataSet #
    def export_dataset(self):
        result = {"nodes": self.nodes, "links": self.links}
        with open(f"./cache/dataset-{self.keyword}-{self.timestamp}.json", 'w',
                  encoding='utf-8') as json_file:
            json.dump(result, json_file, ensure_ascii=False)

        return result
