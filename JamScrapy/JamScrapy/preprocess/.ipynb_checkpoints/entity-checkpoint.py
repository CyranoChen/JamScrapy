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


class Group(Base):
    __tablename__ = 'jam_group_from_post'
    id = Column(Integer, primary_key=True)
    groupname = Column(String(16))
    membercount = Column(Integer)
    memberinfourl = Column(String(16))
    groupurl = Column(String(16))


class Profile(Base):
    __tablename__ = 'jam_profile'
    id = Column(Integer, primary_key=True)
    profileurl = Column(String(16))
    username = Column(String(16))
    displayname = Column(String(16))
    avatar = Column(String(16))
    mobile = Column(String(16))
    email = Column(String(16))
    managers = Column(String(16))
    reports = Column(String(16))
    groups = Column(String(16))
    followers = Column(String(16))
    following = Column(String(16))
