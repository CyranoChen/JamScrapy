from JamScrapy import config
from sqlalchemy import create_engine

engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
results = []
results = engine.execute(
    'SELECT distinct displayname, profileurl FROM jam_people_from_post WHERE displayname <> \'Alumni\' ORDER BY displayname')

print(results)

for r in results:
    print(r[0])
    print(r[1])