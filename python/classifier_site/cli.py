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
from sqlalchemy import or_
import random
import re

manager = Manager(app)


@manager.command
def initdb():
    """
    Creates all database tables.
    """
    db.create_all()
    print 'Initialized the database.'


@manager.command
def dropdb():
    """
    Drops all database tables.
    """
    db.drop_all()
    print 'Dropped the database.'


@manager.command
def restartDb():
    dropdb()
    initdb()


@manager.command
def ipyDebug():
    """
    for testing
    """
    ipy.embed()


@manager.option('-c', '--chunk', dest='chunk', help='Specify a chunk [0, 1, 2]', required=True)
@manager.option('-p', '--processes', dest='num_processes', help='Specify number of processes to use', required=False)
def loadBusinesses(chunk, num_processes=cpu_count()):
    assert chunk in ['0', '1', '2'], "Chunk must be 0, 1, or 2"
    businesses = loader.get_challengeset(int(chunk))
    total = len(businesses)

    pool = Pool(processes=num_processes)

    print "Loading {} businesseses".format(total)
    i = 0
    for group in chunker(businesses, num_processes):
        i += len(group)
        sys.stdout.write('\r')
        sys.stdout.write("[%-50s] %d%% (%d/%d) " % ('=' * ((i + 1)
                                                           * 50 / total), ((i + 1) * 100 / total), i + 1, total))
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
def classifyBusinessWithScorer(scorer=TfidfScorer()):
    businessPage = Business.query.paginate(1, 500, True)
    total = businessPage.total
    i = 0
    while True:
        for b in businessPage.items:
            i += 1
            sys.stdout.write('\r')
            sys.stdout.write("[%-50s] %d%% (%d/%d) " % ('=' * ((i + 1)
                                                               * 50 / total), ((i + 1) * 100 / total), i, total))
            sys.stdout.flush()
            code = scoreLogic3(b, scorer.score_business(b))
            writeClassification(b.unique_id, code)
        if businessPage.has_next:
            businessPage = businessPage.next()
        else:
            break


def scoreLogic1(scores):
    """
    argmax
    """
    return scores[0][1]


def scoreLogic2(scores, threshold=.7):
    """
    agrmax if score is above THRESHOLD, else nothing
    """
    if scores[0][0] > .7:
        return scores[0][1]
    else:
        return ''


def scoreLogic3(b, scores, threshold=.7):
    topMatch = naics_dict[scores[0][1]]
    matches = re.findall(r'\(except(.+?)\)', topMatch['title'] + " " + topMatch['description'])
    matches = sum([m.strip().split() for m in matches], [])
    black_list = ['of', 'the', 'in', 'for', 'at', 'and', 'or', 'as', 'on', 'real']
    idx = 0
    for m in matches:
        if m in black_list:
            continue
        if m in b.name:
            print m
            idx = 1
            break
    if scores[idx][0] > .7:
        return scores[idx][1]
    else:
        return ''

@manager.command
def stochasticgradientdescent():
  weights = util.sample_weights(8,100)
  index_to_id = loader.get_index_to_id()
  id_to_bizid = loader.get_id_to_bizid()
  S = loader.get_S()

  WEIGHTS_DICT = {'prior': 0.12000000000000001, 'd_t_sim': 0.16000000000000003, 't_d_sim': 0.18000000000000002, 'd_d_w2vsim': 0.12000000000000001, 't_t_sim': 0.32, 't_d_w2vsim': 0.1, 'd_t_w2vsim': 0.08, 't_t_w2vsim': 0.14, 'd_d_sim': 0.1}
  
  for _ in range(10000):
    for k in WEIGHTS_DICT.keys():
      
      sc = -float("inf")
      best_dev = .02
      base = WEIGHTS_DICT[k]
      for dev in [.02,0,-.02]:
        WEIGHTS_DICT[k] = base + dev

        w = []
        for i,j in enumerate(['d_d_sim', 'd_d_w2vsim', 'd_t_sim', 'd_t_w2vsim', 't_d_sim', 't_d_w2vsim', 't_t_sim', 't_t_w2vsim', 'prior']):
          w.append(WEIGHTS_DICT[j])

        S_prime = [S[i]*w[i] for i in range(len(S))]
        S_prime = reduce(lambda x,y:x+y, S_prime)
        for i in range(10000):
          argmax = np.argmax(S_prime[i,:])
          ide = index_to_id[argmax]
          writeClassification(id_to_bizid[i], ide)
        score = getPredictionScoreOfTrainingSet()
        if score > sc:
          sc = score
          best_dev = dev
        print sc

      WEIGHTS_DICT[k] = base + best_dev
      w = []
      for i,j in enumerate(['d_d_sim', 'd_d_w2vsim', 'd_t_sim', 'd_t_w2vsim', 't_d_sim', 't_d_w2vsim', 't_t_sim', 't_t_w2vsim', 'prior']):
        w.append(WEIGHTS_DICT[j])
      S_prime = [S[i]*w[i] for i in range(len(S))]
      S_prime = reduce(lambda x,y:x+y, S)
      for i in range(10000):
        ide = index_to_id[np.argmax(S_prime[i,:])]
        writeClassification(id_to_bizid[i], ide)
      score = getPredictionScoreOfTrainingSet()
      if score > sc:
        sc = score
        best_dev = dev
      print sc
      print WEIGHTS_DICT


@manager.option('-s', '--samples', dest='samples', help='Numbers of random weight samples', required=False)
def classifyBusinesses(samples=1):
    samples = int(samples)
    WEIGHTS_DICT = {
        'd_d_sim':  0.862052344506,
        't_t_sim': 1.5,
        'd_t_sim': 0.7694268978,
        't_d_sim': 1.0,
        't_t_w2vsim': 0.0,
        'd_d_w2vsim': 0.0,
        'd_t_w2vsim': 0.0,
        't_d_w2vsim': 0.0
    }
    THRESHOLD = .6 # [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]

    # buzz words
    ids_with_redbox = ids_for_query('redbox', ['name'])
    ids_with_restaurant = ids_for_query('restaurant', ['name', 'business_type', 'description'])
    ids_with_vet = ids_for_query('veterinary', ['name', 'business_type', 'description'])
    ids_with_dentist = ids_for_query('dentist', ['name', 'business_type', 'description']) \
        + ids_for_query('dental', ['name', 'business_type', 'description'])
    ids_with_bank = ids_for_query('bank', ['business_type'])
    ids_with_car_repair = ids_for_query('car%repair', ['name', 'business_type'])
    ids_with_landscaping = ids_for_query('landscap', ['name', 'business_type'])
    ids_with_locksmith = ids_for_query('locksmith', ['name', 'business_type'])
    ids_with_hotel = ids_for_query('hotel', ['name', 'business_type']) \
        + ids_for_query('motel', ['name', 'business_type'])
    ids_with_photo = ids_for_query('photo', ['name', 'business_type'])

    for threshold in xrange(samples):
        # d_d_sim = random.random()
        # t_t_sim = 1.5
        # d_t_sim = random.random()
        # t_d_sim = 1.0
        # WEIGHTS_DICT = {
        #    'd_d_sim': d_d_sim,
        #    't_t_sim': t_t_sim,
        #    'd_t_sim': d_t_sim,
        #    't_d_sim': t_d_sim,
        #    't_t_w2vsim': 0.0,
        #    'd_d_w2vsim': 0.0,
        #    'd_t_w2vsim': 0.0,
        #    't_d_w2vsim': 0.0
        # }
        column_to_code = loader.get_index_to_id()
        row_to_bizid = loader.get_id_to_bizid()
        S = loader.get_S()

        features_list = ['d_d_sim', 'd_d_w2vsim', 'd_t_sim', 'd_t_w2vsim', 't_d_sim', 't_d_w2vsim', 't_t_sim', 't_t_w2vsim']
        w = [WEIGHTS_DICT[k] for k in features_list]
        S = [Si*wi for Si, wi in zip(S, w)]
        S = reduce(lambda x,y:x+y, S)
        for i in xrange(10000):
            bizid = row_to_bizid[i]
            if bizid in ids_with_redbox:
                code = 532230
            elif bizid in ids_with_restaurant:
                code = 72251
            elif bizid in ids_with_vet:
                code = 541940
            elif bizid in ids_with_dentist:
                code = 621210
            elif bizid in ids_with_bank:
                code = 52
            elif bizid in ids_with_car_repair:
                code = 811111
            elif bizid in ids_with_landscaping:
                code = 561730
            elif bizid in ids_with_locksmith:
                code = 561622
            elif bizid in ids_with_hotel:
                code = 721110
            elif bizid in ids_with_photo:
                code = 541921
            else:
                code = column_to_code[np.argmax(S[i,:])]
                score = np.max(S[i,:])
                if score > THRESHOLD:
                    code = column_to_code[np.argmax(S[i,:])]
                else:
                    code = '' # no guess
            writeClassification(row_to_bizid[i], code)
        # print d_d_sim, t_t_sim, d_t_sim, t_d_sim
        predictionScoreOfTrainingSet()


@manager.command
def predictionScoreOfTrainingSet():
    hand_classified_set = loader.get_hand_classifiedset()
    algo_classified_set = loader.get_algo_classifiedset()
    total = 0
    scores = []
    for uid, actual in hand_classified_set.iteritems():
        guess = algo_classified_set[uid]
        scores.append(util.score_prediction(guess, actual))
    total = sum(scores)
    max_potential = len(hand_classified_set.keys()) * 6
    print "Score: ", total
    print "Total: ", max_potential
    print "%: ", total / float(max_potential)
    unique, counts = np.unique(scores, return_counts=True)
    print "Frequencies: \n", np.asarray((unique, counts)).T


def writeClassification(business_uid, naics_code):
    loader.write_row_algo_classified_set(business_uid, naics_code)


def ids_for_query(string, attributes):
    regex = '%{}%'.format(string)
    conditions = [getattr(Business, attr).ilike(regex) for attr in attributes]
    condition = or_(*conditions)
    ids = db.session.query(Business.unique_id).filter(condition).all()
    if len(ids) == 0:
        return []
    return list(zip(*ids)[0])

if __name__ == "__main__":
    naics_items = loader.get_naics_data_for_level(6)
    business_types = loader.get_business_types()
    naics_dict = loader.get_naics_dict()
    manager.run()
