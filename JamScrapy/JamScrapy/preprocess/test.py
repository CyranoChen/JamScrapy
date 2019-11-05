import scrapy

from tqdm import tqdm

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from JamScrapy import config
from JamScrapy.preprocess.entity import PortalProfile


def process_profiles():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()
    profile = session.query(PortalProfile).filter(PortalProfile.username == 'C5095629').first()
    print(profile.username, profile.displayname)



if __name__ == '__main__':
    count = process_profiles()
    print('Duplicate:', count)

    print("All Done")
