from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from JamScrapy import config
from JamScrapy.preprocess.entity import Profile, PortalProfile, PeoplePorfile

def fill_people_porfile_fields():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

    results = engine.execute(
        f"update jam_people_from_post a inner join jam_post b on a.posturl=b.url set a.postid=b.id where a.keyword='{KEYWORD}' and b.keyword='{KEYWORD}'")

    return

if __name__ == '__main__':
    fill_people_porfile_fields()

    print('All Done')