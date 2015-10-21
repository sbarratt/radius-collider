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
from collections import OrderedDict
from random import shuffle
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
        sys.stdout.write("[%-50s] %d%% (%d/%d) " % ('=' * ((i + 1) * 50 / total), ((i + 1) * 100 / total), i + 1, total))
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
def stochasticgradientdescent():
    index_to_id = loader.get_index_to_id()
    id_to_bizid = loader.get_id_to_bizid()
    S = loader.get_S()

    WEIGHTS_DICT = OrderedDict([
        ('d_d_sim',  0.1),
        ('d_d_w2vsim', 0.12000000000000001),

        ('d_t_sim', 0.16000000000000003),
        ('d_t_w2vsim', 0.08),

        ('t_d_sim', 0.18000000000000002),
        ('t_d_w2vsim', 0.1),

        ('t_t_sim', 0.32),
        ('t_t_w2vsim', 0.14),

        ('prior', 0.12000000000000001)
    ])

    for _ in xrange(10000):
        for k in shuffle(WEIGHTS_DICT.keys()):

            sc = -float("inf")
            best_dev = .02
            base = WEIGHTS_DICT[k]
            for dev in [.02, 0, -.02]:
                WEIGHTS_DICT[k] = base + dev

                w = WEIGHTS_DICT.values()

                S_prime = [Si * wi for Si, wi in zip(S, w)]
                S_prime = reduce(lambda x, y: x + y, S_prime)
                for i in xrange(10000):
                    argmax = np.argmax(S_prime[i, :])
                    ide = index_to_id[argmax]
                    writeClassification(id_to_bizid[i], ide)
                score = getPredictionScoreOfTrainingSet()
                if score > sc:
                    sc = score
                    best_dev = dev
                print sc

            WEIGHTS_DICT[k] = base + best_dev
            w = WEIGHTS_DICT.values()

            S_prime = [Si * wi for Si, wi in zip(S, w)]
            S_prime = reduce(lambda x, y: x + y, S)
            for i in xrange(10000):
                ide = index_to_id[np.argmax(S_prime[i, :])]
                writeClassification(id_to_bizid[i], ide)
            score = predictionScoreOfTrainingSet()
            if score > sc:
                sc = score
                best_dev = dev
            print sc
            print WEIGHTS_DICT



@manager.option('-s', '--samples', dest='samples', help='Numbers of random weight samples', required=False)
def classifyBusinesses(samples=1):
    samples = int(samples)
    # ORDER: 'd_d_sim', 'd_d_w2vsim', 'd_t_sim', 'd_t_w2vsim', 't_d_sim', 't_d_w2vsim', 't_t_sim', 't_t_w2vsim', 'prior'
    WEIGHTS_DICT = OrderedDict([
        ('d_d_sim',  0.862052344506),
        ('d_d_w2vsim', 0.1),

        ('d_t_sim', 0.7694268978),
        ('d_t_w2vsim', 0.1),

        ('t_d_sim', 1.0),
        ('t_d_w2vsim', 0.2),

        ('t_t_sim', 1.5),
        ('t_t_w2vsim', 0.5),

        ('prior', .05)

        # ('t_t_w2vsim', 0.5),
        # ('d_d_w2vsim', 0.1),
        # ('d_t_w2vsim', 0.1),
        # ('t_d_w2vsim', 0.2),
    ])
    # THRESHOLDS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]
    THRESHOLD = 1.1

    # buzz words
    ids_with_redbox = ids_for_query('redbox', ['name'])
    ids_with_restaurant = ids_for_query('restaurant', ['name', 'business_type', 'description'])
    ids_with_vet = ids_for_query('veterinary', ['name', 'business_type', 'description'])
    ids_with_insurance = ids_for_query('insurance', ['name', 'business_type'])
    ids_with_dentist = ids_for_query('dentist', ['name', 'business_type', 'description']) \
        + ids_for_query('dental', ['name', 'business_type', 'description'])
    ids_with_bank = ids_for_query('bank', ['business_type'])
    ids_with_car_repair = ids_for_query('car%repair', ['name', 'business_type'])
    ids_with_landscaping = ids_for_query('landscap', ['name', 'business_type'])
    ids_with_locksmith = ids_for_query('locksmith', ['name', 'business_type'])
    ids_with_hotel = ids_for_query('hotel', ['name', 'business_type']) \
        + ids_for_query('motel', ['name', 'business_type'])
    ids_with_photo = ids_for_query('photo', ['name', 'business_type'])

    for _ in xrange(samples):
        print THRESHOLD
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

        S = [Si * wi for Si, wi in zip(S, WEIGHTS_DICT.values())]
        S = reduce(lambda x, y: x + y, S)
        for i in xrange(10000):
            bizid = row_to_bizid[i]
            if bizid in ids_with_redbox:
                code = 532230
            elif bizid in ids_with_restaurant:
                code = 72251
            elif bizid in ids_with_vet:
                code = 541940
            elif bizid in ids_with_insurance:
                code = 524210
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
                code = column_to_code[np.argmax(S[i, :])]
                score = np.max(S[i, :])
                if score > THRESHOLD:
                    code = column_to_code[np.argmax(S[i, :])]
                else:
                    code = ''  # no guess
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
    max_potential = len(hand_classified_set.keys()) * 6.0
    print "Score: ", total
    print "Total: ", max_potential
    print "%: ", total / float(max_potential)
    unique, counts = np.unique(scores, return_counts=True)
    print "Frequencies: \n", np.asarray((unique, counts)).T


def getPredictionScoreOfTrainingSet():
    hand_classified_set = loader.get_hand_classifiedset()
    algo_classified_set = loader.get_algo_classifiedset()
    total = 0
    scores = []
    for uid, actual in hand_classified_set.iteritems():
        guess = algo_classified_set[uid]
        scores.append(util.score_prediction(guess, actual))
    total = sum(scores)
    max_potential = len(hand_classified_set.keys()) * 6
    return total / float(max_potential)


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
