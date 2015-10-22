from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from db import db
import dbHelper as dbh
import loader
from flask.ext.script import Manager
from app import app
import util
from multiprocessing import Pool, cpu_count
import IPython as ipy
import numpy as np

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
    # late import
    from scorers import StochasticDescent
    StochasticDescent()

@manager.command
def classifyBusinesses():
    # late import
    from scorers import Classifier

    for thresh in np.arange(0, .6, .05):
        classifier = Classifier(threshhold=thresh)
        classifcations = classifier.classify(rule_based=True)
        loader.write_rows_algo_classified_set(classifcations)
        predictionScoreOfTrainingSet()

@manager.command
def predictionScoreOfTrainingSet():
    # late import
    from scorers import Scorer
    scorer = Scorer()

    total, max_potential, frequencies = scorer.scoreClassifications()

    print "Score: ", total
    print "Total: ", max_potential
    print "%: ", total / float(max_potential)
    print "Frequencies: \n", frequencies


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
