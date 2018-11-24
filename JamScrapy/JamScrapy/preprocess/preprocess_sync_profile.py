from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from JamScrapy.preprocess.entity import Profile, PortalProfile

# TODO modify the value of field assistant of table people_profile
sql = '''
Insert into people_profile(profileurl,username,displayname,avatar,mobile,email,phone,address,managers,reports,groups,followers,following,
                           boardarea,functionalarea,costcenter,officelocation,localinfo,assistant) 
  select j.profileurl, j.username, j.displayname, j.avatar, p.mobile, p.email, p.phone, p.address, j.managers, j.reports, j.groups, j.followers, j.following,
    p.boardarea, p.functionalarea, p.costcenter, p.officelocation, p.localinfo, p.assistant 
from jam_profile j left outer join portal_profile p 
    on j.username = p.username where j.username not in (select username from people_profile)  

'''


DB_CONNECT_STRING_LOCAL = 'mysql+pymysql://root:Initial0@127.0.0.1:3306/scrapy?charset=utf8mb4'
DB_CONNECT_STRING_SERVER = 'mysql+pymysql://root:Initial0@10.58.78.253:3306/nexus?charset=utf8mb4'

engine_l = create_engine(DB_CONNECT_STRING_LOCAL, max_overflow=5)
engine_s = create_engine(DB_CONNECT_STRING_SERVER, max_overflow=5)

session_l = sessionmaker(bind=engine_l)()
session_s = sessionmaker(bind=engine_s)()

## jam_profiles


profiles_exist = engine_s.execute("select username from jam_profile")

print('profiles server', profiles_exist.rowcount)

exist = []
for p in profiles_exist:
    exist.append(p.username)

jam_profiles = engine_l.execute("select * from jam_profile")

print('jam_profiles local', jam_profiles.rowcount)

count = 0
for p in jam_profiles:
    if p.username not in exist:
        print(p.id, p.username, p.displayname)
        profile_s = Profile(
            profileurl=p.profileurl.strip(),
            username=p.username.strip(),
            displayname=p.displayname.strip(),
            avatar=p.avatar,
            mobile=p.mobile,
            email=p.email,
            managers=p.managers,
            reports=p.reports,
            groups=p.groups,
            followers=p.followers,
            following=p.following
        )
        session_s.add(profile_s)
        count += 1

print(count)

## portal_profiles

profiles_exist = engine_s.execute("select username from portal_profile")

print('profiles server', profiles_exist.rowcount)

exist = []
for p in profiles_exist:
    exist.append(p.username)

portal_profiles = engine_l.execute("select * from portal_profile")

print('portal_profiles local', portal_profiles.rowcount)

count = 0
for p in portal_profiles:
    if p.username not in exist:
        print(p.id, p.username, p.displayname)
        profile_s = PortalProfile(
            profileurl=p.profileurl.strip(),
            username=p.username.strip(),
            displayname=p.displayname.strip(),
            boardarea=p.boardarea,
            functionalarea=p.functionalarea,
            costcenter=p.costcenter,
            officelocation=p.officelocation,
            manager=p.manager,
            localinfo=p.localinfo,
            email=p.email,
            phone=p.phone,
            mobile=p.mobile,
            address=p.address,
            assistant=p.assistant
        )
        session_s.add(profile_s)
        count += 1

print(count)

session_l.commit()
session_l.close()

session_s.commit()
session_s.close()
