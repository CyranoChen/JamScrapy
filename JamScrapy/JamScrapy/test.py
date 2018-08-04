from JamScrapy import config
from sqlalchemy import create_engine, text

engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

person = dict()
person["name"] = "blockch'ain"
person["role"] = 'crea"tor'

result = engine.execute(
    text("SELECT count(*) FROM jam_people_from_post WHERE 1=1 or keyword = :name or roletype = :role"),
    {"name": person["name"], "role": person["role"]})

print(result.first()[0])
