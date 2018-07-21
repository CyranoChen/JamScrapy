from JamScrapy import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from JamScrapy.preprocess.entity import Profile, PortalProfile
import ast
import json

request_urls =[]

engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
results = engine.execute(f"select * from spider_jam_search where body <> '[]' and keyword = '{config.KEYWORD}'")

print('total search pages', results.rowcount)

for r in results:
    request_urls.extend(ast.literal_eval(r.topics))

set_request_urls = set()
for r in request_urls:
    set_request_urls.add(r.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', ''))

# 全部不重复的URL set
print('total distinct post url', len(set_request_urls), '/', len(request_urls))

set_exist_urls = set()
results = engine.execute(f"select distinct url from jam_post where keyword = '{config.KEYWORD}'")

for r in results:
    set_exist_urls.add(r.url.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', ''))

request_urls = list(set_request_urls - set_exist_urls)

        # 最终需要爬取的URL
print('exist + require', len(set_exist_urls), '+' ,len(request_urls))