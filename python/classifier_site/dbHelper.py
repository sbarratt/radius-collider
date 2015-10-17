from db import db
from models import Business

def addBusiness(business, business_type, six_code_guesses, three_code_buckets):
  biz = Business(business, business_type, six_code_guesses, three_code_buckets)
  db.session.add(biz)
  db.session.commit()

def getBusinessPage(page):
  return Business.query.paginate(page, 20, True)
