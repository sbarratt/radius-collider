from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from db import db
import dbHelper as dbh
import loader
from flask.ext.script import Manager
from models import Business
from app import app
from scorers import TfidfScorer
import util
import numpy as np

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
    print i, b['unique_id']
    features_dict = TfidfScorer.get_features(b, naics_items, ADD_SYNONYMS=True)
    business_type = business_types.get(b['unique_id'].encode())
    dbh.addBusiness(b, business_type, features_dict)


@manager.command
def getOptimalWeights():
  # TODO weights_grid
  weights_grid = util.get_weights_grid()
  scores = []
  for weights in weights_grid:
    scorer = TfidfScorer(weights)
    loader.reset_algo_classifiedset()
    classifyBusinessWithScorer(scorer)
    preditionScore = predictionScoreOfTrainingSet()
    scores.append(preditionScore)
    print "\n\nScore", preditionScore
    print "Weights", weights
  print "\n\n--------------------------------------------"
  print "Best Score", max(scores)
  print "Best Weights", weights_grid[np.argmin(scores)]


def classifyBusinessWithScorer(scorer):
  businessPage = Business.query.paginate(1, 10, True)
  i = 0
  while True:
    for b in businessPage.items:
      i += 1
      print i
      writeClassification(b.unique_id, scorer.score_business(b)[0][1])
    if businessPage.has_next:
      businessPage = businessPage.next()
    else:
      break

def predictionScoreOfTrainingSet():
  hand_classified_set = loader.get_hand_classified_set()
  algo_classified_set = loader.get_algo_classified_set()
  score = 0
  for uid, actual in hand_classified_set:
    guess = algo_classified_set[uid]
    score += util.score_prediction(guess, actual)
  total = len(hand_classified_set.keys())*6
  print "Score: " + score
  print "Total: " + total
  print "%: " + score/float(total)

def writeClassification(business_uid, naics_code):
  loader.write_row_algo_classified_set(business_uid, naics_code)

@manager.command
def restartDb():
  dropdb()
  initdb()

if __name__ == "__main__":
  manager.run()
