from JamScrapy import config
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from JamScrapy.preprocess.entity import People

DB_CONNECT_STRING_LOCAL = 'mysql+pymysql://root:Initial0@10.178.200.23:3306/nexus?charset=utf8mb4'
DB_CONNECT_STRING_SERVER = 'mysql+pymysql://root:Initial0@10.58.78.253:3306/nexus?charset=utf8mb4'

engine_l = create_engine(DB_CONNECT_STRING_LOCAL, max_overflow=5)
engine_s = create_engine(DB_CONNECT_STRING_SERVER, max_overflow=5)

session_l = sessionmaker(bind=engine_l)()
session_s = sessionmaker(bind=engine_s)()

sql = "select * from jam_people_from_post where keyword = 'innovation' and id > 900000 order by id"
results = engine_s.execute(sql).fetchall()

print('post on server', len(results))

count = 0
for r in tqdm(results):
    people_l = People(
        username = r.username,
        displayname = r.displayname,
        postid = r.postid,
        posturl = r.posturl,
        position = r.position,
        profileurl = r.profileurl,
        roletype = r.roletype,
        keyword = r.keyword
    )
    session_l.add(people_l)
    count += 1

print('people imported:', count)

session_l.commit()
session_l.close()
