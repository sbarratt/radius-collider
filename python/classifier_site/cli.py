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
from multiprocessing import Pool, cpu_count
import IPython as ipy

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
def getAllBusinesses():
  ipy.embed()

@manager.option('-c', '--chunk', dest='chunk', help='Specify a chunk [0, 1, 2]', required=True)
def loadBusinesses(chunk):
  assert chunk in ['0', '1', '2'], "Chunk must be 0, 1, or 2"
  businesses = loader.get_challengeset(int(chunk))
  total = len(businesses)

  num_processes = cpu_count()
  pool = Pool(processes=num_processes)

  print "Loading {} businesseses".format(total)
  i = 0
  for group in chunker(businesses, num_processes):
    i += len(group)
    sys.stdout.write('\r')
    sys.stdout.write("[%-50s] %d%% (%d/%d) " % ('='*((i+1)*50/total), ((i+1)*100/total), i + 1, total))
    sys.stdout.flush()
    pool.map(concurrent_process, group)


def concurrent_process(biz):
  if dbh.businessExists(biz['unique_id']):
    return
  features_dict = TfidfScorer.get_features(biz, naics_items, ADD_SYNONYMS=True)
  business_type = business_types.get(biz['unique_id'].encode())
  dbh.addBusiness(biz, business_type, features_dict)


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

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
  total = businessPage.total
  i = 0
  while True:
    for b in businessPage.items:
      i += 1
      sys.stdout.write('\r')
      sys.stdout.write("[%-50s] %d%% (%d/%d) " % ('='*((i+1)*50/total), ((i+1)*100/total), i + 1, total))
      sys.stdout.flush()
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
  naics_items = loader.get_naics_data_for_level(6)
  business_types = loader.get_business_types()
  manager.run()
