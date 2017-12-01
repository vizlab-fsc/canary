import os
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Table, Column, DateTime, Integer, String, ForeignKey, relationship

engine = create_engine(os.environ['DATABASE_URI'])
Base = declarative_base()
Session = sessionmaker(bind=engine)


images_tags = Table('images_tags', Base.metadata,
    Column('image_id', Integer, ForeignKey('images.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)


class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    url = Column(String)
    key = Column(String)
    hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow())
    tags = relationship('Tag', secondary=images_tags, backref='images')
    usages = relationship('ImageUsage', backref='image')


class ImageUsage(Base):
    __tablename__ = 'image_usages'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow())
    image_id = Column(Integer, ForeignKey('images.id'))
    context_id = Column(Integer, ForeignKey('contexts.id'))


class Context():
    __tablename__ = 'contexts'

    lid = Column(String)
    url = Column(String)
    author = Column(String)
    content = Column(String)
    timestamp = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow())
    source_id = Column(Integer, ForeignKey('sources.id'))
    usages = relationship('ImageUsage', backref='context')


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String)


class Source(Base):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    contexts = relationship('Context', backref='source')


Base.metadata.create_all(engine)
