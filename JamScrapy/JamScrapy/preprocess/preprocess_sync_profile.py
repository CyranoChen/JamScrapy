# Insert the new portal profile, run it first
sql = '''
Insert into people_profile(profileurl,username,displayname,avatar,mobile,email,phone,address,managers,reports,groups,followers,following,
                           boardarea,functionalarea,costcenter,officelocation,localinfo,assistant) 
  select j.profileurl, j.username, j.displayname, j.avatar, p.mobile, p.email, p.phone, p.address, p.manager, j.reports, j.groups, j.followers, j.following,
    p.boardarea, p.functionalarea, p.costcenter, p.officelocation, p.localinfo, p.assistant 
from jam_profile j left outer join portal_profile p 
    on j.username = p.username where j.username not in (select username from people_profile)  

'''

from JamScrapy import config
from sqlalchemy import create_engine, text
from tqdm import tqdm

import json

engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
NOT_FOUND_PROFILEURL = set()
#
#
# def build_profile_field_by_url(field, dict_profileurl):
#     ret_list = []
#     if field:
#         json_list = json.loads(field)
#         for item in json_list:
#             url = item['url'].split('/')[-1]
#             if url in dict_profileurl:
#                 ret_list.append({'name': item['name'], 'username': dict_profileurl[url]})
#             else:
#                 NOT_FOUND_PROFILEURL.add(url)
#                 print(item, 'not found')
#
#     return json.dumps(ret_list) if len(ret_list) > 0 else None
#
#
# # Initial the dictionary of latest portal_profile
# sql = "select username, managers, reports, followers, following, groups from jam_profile"
# results = engine.execute(sql)
#
# dict_jam_profile = dict()
# for row in results:
#     dict_jam_profile[row.username] = row
#
# print('dict_jam_profile:', len(dict_jam_profile))
#
# # Get the people_profile
# sql = "select id, profileurl, username from people_profile order by id"
# results = engine.execute(sql)
#
# # Initial the dictionary of profile url and build the list of portal
# dict_profileurl = dict()
# list_people = []
# for row in results:
#     uid = row.profileurl.split('/')[-1]
#     dict_profileurl[uid] = row.username
#     list_people.append({'id': row.id, 'username': row.username})
#
# print('dict_profileurl:', len(dict_profileurl), 'list_people', len(list_people))
#
# count_not_found = 0
# for p in tqdm(list_people):
#     if p['username'] in dict_jam_profile:
#         p_jam = dict_jam_profile[p['username']]
#
#         # print(p_jam.username, p_jam.managers, p_jam.reports, p_jam.followers, p_jam.following)
#         managers = build_profile_field_by_url(p_jam['managers'], dict_profileurl)
#         reports = build_profile_field_by_url(p_jam['reports'], dict_profileurl)
#         followers = build_profile_field_by_url(p_jam['followers'], dict_profileurl)
#         following = build_profile_field_by_url(p_jam['following'], dict_profileurl)
#         groups = json.dumps(json.loads(p_jam['groups'])) if p_jam['groups'] else None
#         # print(p_jam.username, managers, reports, followers, following)
#
#         sql = '''update people_profile set managers=:managers, reports=:reports,
#                 groups=:groups, followers=:followers, following=:following
#                 where id=:id and username=:username '''
#         para = {'managers': managers, 'reports': reports, 'groups': groups,
#                 'followers': followers, 'following': following, 'id': int(p['id']), 'username': p['username']}
#         engine.execute(text(sql), para)
#     else:
#         count_not_found += 1
#         print(p['username'], ' not found')
#
# print('count_not_found:', count_not_found)
#
# print('NOT_FOUND_PROFILEURL:', len(NOT_FOUND_PROFILEURL))
#
# with open('../../output/not_found_profileurl.json', 'w', encoding='utf-8') as json_file:
#     json.dump(list(NOT_FOUND_PROFILEURL), json_file, ensure_ascii=False)

sql = "select id, username, manager, assistant from portal_profile where manager is not null or assistant is not null order by id"
results = engine.execute(sql).fetchall()

for r in tqdm(results):
    sql = '''update people_profile set managers=:managers, assistant=:assistant where username=:username'''
    para = {'managers': r.manager, 'assistant': r.assistant, 'username': r.username}
    engine.execute(text(sql), para)
