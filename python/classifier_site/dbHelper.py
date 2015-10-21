from db import db
from models import Business

def addBusiness(business, business_type, features_dict):
  biz = Business(business, business_type, features_dict)
  db.session.add(biz)
  db.session.commit()

def getBusinessPage(page):
  return Business.query.paginate(page, 20, True)

def getAllBusinesses():
  return Business.query.all()

def getBusinessWithId(id):
  return Business.query.filter_by(unique_id=str(id)).first()

def businessExists(id):
  return Business.query.filter_by(unique_id=str(id)).count() > 0

def getNextUnclassifiedBusiness(unclassified_set):
  while True:
    next_id = unclassified_set.pop()
    if businessExists(next_id):
      return getBusinessWithId(next_id)
  return None

def getFirstBusiness():
  return Business.query.first()
  # return Business.query.all()[9]

