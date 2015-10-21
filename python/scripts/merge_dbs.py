from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, PickleType, Text
import os
import sys

Base = declarative_base()


class Business(Base):
    __tablename__ = 'Business'
    id = Column(Integer, primary_key=True)
    unique_id = Column(String(80))
    name = Column(String(80))
    address = Column(String(80))
    description = Column(Text)
    website = Column(String(40))
    business_type = Column(String(40))
    features_dict = Column(PickleType)

    def __init__(self, unique_id, name, address, description, website, business_type, features_dict):
        self.unique_id = unique_id
        self.name = name
        self.address = address
        self.description = description
        self.website = website
        self.business_type = business_type
        self.features_dict = features_dict

    def __repr__(self):
        return '<Business %r>' % self.name


basedir = os.path.abspath(os.path.dirname(__file__))

dbMyles = create_engine(
    'sqlite:///' + os.path.join(basedir, 'dbs/app_myles.db'))
dbAlex = create_engine('sqlite:///' + os.path.join(basedir, 'dbs/app_alex.db'))
dbShane = create_engine(
    'sqlite:///' + os.path.join(basedir, 'dbs/app_shane.db'))

dbMylesSession = sessionmaker(dbMyles)()
dbAlexSession = sessionmaker(dbAlex)()
dbShaneSession = sessionmaker(dbShane)()

mylesBusinesses = dbMylesSession.query(Business).all()
alexBusinesses = dbAlexSession.query(Business).all()
shaneBusinesses = dbShaneSession.query(Business).all()


dbAll = create_engine('sqlite:///' + os.path.join(basedir, 'dbs/app_all.db'))
dbAllSession = sessionmaker(dbAll)()
Base.metadata.create_all(bind=dbAll)

for session in [dbMylesSession, dbAlexSession, dbShaneSession]:
    businessPage = session.query(Business).paginate(1, 100, True)
    total = businessPage.total
    i = 0
    while True:
        for b in businessPage.items:
            i += 1
            sys.stdout.write('\r')
            sys.stdout.write("[%-50s] %d%% (%d/%d) " % ('=' * ((i + 1)
                                                               * 50 / total), ((i + 1) * 100 / total), i + 1, total))
            sys.stdout.flush()
            biz = Business(b.unique_id, b.name, b.address, b.description,
                           b.website, b.business_type, b.features_dict)
            dbAllSession.add(biz)
        dbAllSession.commit()
        if businessPage.has_next:
            businessPage = businessPage.next()
        else:
            break
    print '\n'

print "Done"
