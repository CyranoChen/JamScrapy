from JamScrapy import config
from sqlalchemy import create_engine
import ast

engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

# 开始URL
request_urls = []

engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
results = engine.execute(f"select * from spider_jam_search where body <> '[]' and keyword = '{config.KEYWORD}'")

print('results', results.rowcount)

for r in results:
    request_urls.extend(ast.literal_eval(r.topics))

# 全部URL
print(len(request_urls))

set_request_urls = set()
for r in request_urls:
    set_request_urls.add(r)

# 全部不重复的URL set
print(len(set_request_urls))

set_exist_urls = set()
results = engine.execute(f"select baseurl from spider_jam_post where keyword = '{config.KEYWORD}'")

for r in results:
    set_exist_urls.add(r.baseurl)

# 全部已存在的URL set
print(len(set_exist_urls))

request_urls = list(set_request_urls - set_exist_urls)

# 最终需要爬取的URL
print(len(request_urls))

