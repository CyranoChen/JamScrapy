from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint, Index

import json

Base = declarative_base()


class Post(Base):
    __tablename__ = 'jam_post'
    id = Column(Integer, primary_key=True)
    url = Column(String(16))
    title = Column(String(16))
    author = Column(String(16))
    category = Column(String(16))
    recency = Column(String(16))
    tag = Column(String(16))
    content = Column(String(64))
    comments = Column(Integer)
    likes = Column(Integer)
    views = Column(Integer)
    keyword = Column(String(16))


class People(Base):
    __tablename__ = 'jam_people_from_post'
    id = Column(Integer, primary_key=True)
    username = Column(String(16))
    displayname = Column(String(16))
    postid = Column(Integer)
    posturl = Column(String(16))
    position = Column(Integer)
    profileurl = Column(String(16))
    roletype = Column(String(16))
    keyword = Column(String(16))


class Group(Base):
    __tablename__ = 'jam_group_from_post'
    id = Column(Integer, primary_key=True)
    groupname = Column(String(16))
    membercount = Column(Integer)
    memberinfourl = Column(String(16))
    groupurl = Column(String(16))
    keyword = Column(String(16))


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


class PortalProfile(Base):
    __tablename__ = 'portal_profile'
    id = Column(Integer, primary_key=True)
    profileurl = Column(String(16))
    username = Column(String(16))
    displayname = Column(String(16))
    boardarea = Column(String(16))
    functionalarea = Column(String(16))
    costcenter = Column(String(16))
    officelocation = Column(String(16))
    manager = Column(String(16))
    localinfo = Column(String(16))
    email = Column(String(16))
    phone = Column(String(16))
    mobile = Column(String(16))
    address = Column(String(16))
    assistant = Column(String(16))


class PeoplePorfile(Base):
    __tablename__ = 'people_profile'
    id = Column(Integer, primary_key=True)
    profileurl = Column(String(16))
    username = Column(String(16))
    displayname = Column(String(16))
    displaynameformatted = Column(String(16))
    avatar = Column(String(16))
    mobile = Column(String(16))
    email = Column(String(16))
    phone = Column(String(16))
    address = Column(String(16))
    managers = Column(String(16))
    reports = Column(String(16))
    groups = Column(String(16))
    followers = Column(String(16))
    following = Column(String(16))
    boardarea = Column(String(16))
    functionalarea = Column(String(16))
    costcenter = Column(String(16))
    officelocation = Column(String(16))
    localinfo = Column(String(16))
    assistant = Column(String(16))

class Knowledge(Base):
    __tablename__ = 'jam_knowledge'
    id = Column(Integer, primary_key=True)
    title = Column(String(16))
    abstract = Column(String(64))
    score = Column(Float)