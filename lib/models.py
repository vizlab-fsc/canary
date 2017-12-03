import os
from datetime import datetime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Table, Column, DateTime, Integer, String, ForeignKey
from .domains import domain_for_name

DEFAULT = 'postgresql://canary_user:password@localhost:5432/canary_dev'
engine = create_engine(os.environ.get('DATABASE_URI', DEFAULT))
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

    # additional metadata
    height = Column(Integer)
    width = Column(Integer)
    format = Column(String)
    mode = Column(String)


class ImageUsage(Base):
    __tablename__ = 'image_usages'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow())
    image_id = Column(Integer, ForeignKey('images.id'))
    context_id = Column(Integer, ForeignKey('contexts.id'))


class Context(Base):
    __tablename__ = 'contexts'

    id = Column(Integer, primary_key=True)
    lid = Column(String)
    url = Column(String)
    author = Column(String)
    content = Column(String)
    timestamp = Column(DateTime)
    source_id = Column(Integer, ForeignKey('sources.id'))
    usages = relationship('ImageUsage', backref='context')

    # when this record was created
    # (not when the original post was created)
    created_at = Column(DateTime, default=datetime.utcnow())


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


class Source(Base):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    contexts = relationship('Context', backref='source')

    def api(self):
        return domain_for_name(self.name)


Base.metadata.create_all(engine)
