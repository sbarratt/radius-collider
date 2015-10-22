from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from db import db
import dbHelper as dbh
import loader
from flask.ext.script import Manager
from app import app
import util
import numpy as np
from multiprocessing import Pool, cpu_count
import IPython as ipy
from collections import OrderedDict
from random import shuffle

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
    """
    Restarts the database.
    """
    dropdb()
    initdb()


@manager.command
def ipyDebug():
    """
    Function for testing.
    """
    ipy.embed()

@manager.option('-c', '--chunk', dest='chunk', help='Specify a chunk [0, 1, 2]', required=True)
@manager.option('-p', '--processes', dest='num_processes', help='Specify number of processes to use', required=False)
def loadBusinesses(chunk, num_processes=None):
    assert chunk in ['0', '1', '2'], "Chunk must be 0, 1, or 2"
    businesses = loader.get_challengeset(int(chunk))
    num_processes = int(num_processes) if num_processes else cpu_count()
    total = len(businesses)
    global featurizer
    # late import
    from scorers import Featurizer
    featurizer = Featurizer()

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
    features_dict = featurizer.get_features(biz, naics_items, ADD_SYNONYMS=True)
    business_type = business_types.get(biz['unique_id'].encode())
    dbh.addBusiness(biz, business_type, features_dict)


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))


@manager.command
def stochasticgradientdescent():
    index_to_id = loader.get_index_to_id()
    id_to_bizid = loader.get_id_to_bizid()
    S = loader.get_S()

    WEIGHTS_DICT = OrderedDict([('d_d_sim', 0.1), ('d_d_w2vsim', 0.12000000000000001), 
                 ('d_t_sim', 0.16000000000000003), ('d_t_w2vsim', 0.08), 
                 ('t_d_sim', 0.18000000000000002), ('t_d_w2vsim', 0.1), 
                 ('t_t_sim', 0.34), ('t_t_w2vsim', 0.14), ('prior', 0.12000000000000001)])

    for _ in xrange(10000):
        keys = WEIGHTS_DICT.keys()
        shuffle(keys)
        for k in keys:

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
    # late import
    from scorers import Classifier
    classifier = Classifier()

    classifcations = classifier.classify(rule_based=True)
    print 1
    # loader.write_rows_algo_classified_set(classifcations)
    # predictionScoreOfTrainingSet()


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


if __name__ == "__main__":
    naics_items = loader.get_naics_data_for_level(6)
    business_types = loader.get_business_types()
    naics_dict = loader.get_naics_dict()
    featurizer = None
    manager.run()
