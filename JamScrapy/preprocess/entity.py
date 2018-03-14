from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class Post(Base):
    __tablename__ = 'jam_post_spider'
    id = Column(Integer, primary_key=True)
    baseurl = Column(String(16))
    url = Column(String(16))
    body = Column(String(64))
    createtime = Column(DateTime())


class People(Base):
    __tablename__ = 'jam_people_from_post'
    id = Column(Integer, primary_key=True)
    displayname = Column(String(16))
    postid = Column(Integer)
    posturl = Column(String(16))
    position = Column(Integer)
    profileurl = Column(String(16))
    roletype = Column(String(16))
