from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint, Index

import json

Base = declarative_base()


class SpiderSearch(Base):
    __tablename__ = 'spider_jam_search'

    id = Column(Integer, primary_key=True)
    url = Column(String(16))
    body = Column(String(64))
    topics = Column(String(64))
    createtime = Column(DateTime)
    keyword = Column(String(16))


class SpiderPost(Base):
    __tablename__ = 'spider_jam_post'

    id = Column(Integer, primary_key=True)
    baseurl = Column(String(16))
    url = Column(String(16))
    body = Column(String(64))
    createtime = Column(DateTime)
    keyword = Column(String(16))