from JamScrapy import config
from sqlalchemy import create_engine
import ast

engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

# category = 'documents'
# #
# # results = engine.execute(f"SELECT * FROM spider_jam_post WHERE body IS NOT NULL AND keyword = 'chatbot'"
# # f" AND baseurl like '%%documents%%'")
# #
# # print(results.rowcount)
# #
# # p = results.first()
# # print(p.id)
# # print(p.url)
# # print(p.baseurl)
# # print(p.createtime)

results = engine.execute(f"SELECT * FROM spider_jam_search WHERE body <> '[]' AND keyword = 'blockchain'")

print(results.rowcount)

start_urls = []

for r in results:
    start_urls.extend(ast.literal_eval(r.topics))

print(len(start_urls))