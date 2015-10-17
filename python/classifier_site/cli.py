from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from db import db
import dbHelper as dbh
import util
import loader
from flask.ext.script import Manager
from models import Business
from app import app
import csv

manager = Manager(app)

@manager.command
def initdb():
  """Creates all database tables."""
  db.create_all()
  print('Initialized the database.')

@manager.command
def dropdb():
  """Drops all database tables."""
  db.drop_all()
  print('Dropped the database.')


@manager.command
def loadAllBusinesses():
  businesses = loader.get_challengeset()
  naics_items = loader.get_naics_data_for_level(6)
  business_types = loader.get_business_types()
  i = 0
  for b in businesses:
    i += 1
    print i
    guesses = util.score_business(b, naics_items, ADD_SYNONYMS=True)
    code_list = util.bucket_guesses(guesses)
    business_type = business_types.get(b['unique_id'].encode())
    dbh.addBusiness(b, business_type, guesses, code_list)

@manager.command
def classifyBusinessWithAlgo():
  businessPage = Business.query.paginate(1, 10, True)
  i = 0
  while True:
    for b in businessPage.items:
      i += 1
      print i
      classifyBusiness(b.unique_id, b.six_code_guesses[0][1]['code'])
    if businessPage.has_next:
      businessPage = businessPage.next()
    else:
      break

def classifyBusiness(business_uid, naics_code):
  with open('data/algo_classified_set.csv', 'a') as classified_set:
    wr = csv.writer(classified_set)
    wr.writerow( ( business_uid, naics_code) )

@manager.command
def restartDb():
  dropdb()
  initdb()

if __name__ == "__main__":
  manager.run()
