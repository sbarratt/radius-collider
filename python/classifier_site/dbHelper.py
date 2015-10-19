from db import db
from models import Business

def addBusiness(business, business_type, features_dict):
  biz = Business(business, business_type, features_dict)
  db.session.add(biz)
  db.session.commit()

def getBusinessPage(page):
  return Business.query.paginate(page, 20, True)

def getBusinessWithId(id):
  return Business.query.filter_by(unique_id=str(id)).first()

def businessExists(id):
  return Business.query.filter_by(unique_id=str(id)).count() > 0

def getFirstBusiness():
  return Business.query.first()
  # return Business.query.all()[9]
