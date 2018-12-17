from JamScrapy import config
from sqlalchemy import create_engine, text
from tqdm import tqdm

engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

sql = '''select id, url, username from jam_post'''

results = engine.execute(sql).fetchall()

print('total jam post counts:', len(results))

dict_post = dict((x.url.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', ''), (x.id, x.username)) for x in results)
print(dict_post)

sql = '''select id, postid, postusername, posturl from jam_people_from_post'''

results = engine.execute(sql).fetchall()

for r in tqdm(results):
    url = r.posturl.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', '')
    if url in dict_post:
        postid, postusername = dict_post[url]
        if postid != r.postid or postusername != r.postusername:
            engine.execute(text("update jam_people_from_post set postid=:postid, postusername=:postusername"
                                " where id = :id"), {'postid': postid, 'postusername': postusername, 'id': r.id})
    else:
        engine.execute(text("update jam_people_from_post set postid=null where id = :id"), {'postid': postid, 'id': r.id})
        print(r.id, r.posturl)


# sql = '''select id, username, postusername, posturl from jam_people_from_post where roletype = 'creator' and username is not null '''
# results = engine.execute(sql).fetchall()
#
# print('total jam creators from post counts:', len(results))
#
# dict_post = dict((x.posturl, x.postusername) for x in results)
# print(len(dict_post))
#
# sql = '''select id, postusername, posturl from jam_people_from_post where postusername is null and username is not null'''
# results = engine.execute(sql).fetchall()
#
# for r in tqdm(results):
#     if r.posturl in dict_post:
#         postusername = dict_post[r.posturl]
#         if postusername != r.postusername:
#             engine.execute(text("update jam_people_from_post set postusername=:postusername"
#                                 " where id = :id"), {'postusername': postusername, 'id': r.id})
#     else:
#         print(r.id, r.posturl)