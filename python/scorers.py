#!/usr/bin/env python

"""Scorers
Classes for featurizing and classifying data points.
"""

import util
import loader
from collections import OrderedDict
import numpy as np
from classifier_site.dbHelper import ids_for_query
from random import shuffle

# mapping from matrix elements to codes and business ids
column_to_code = loader.get_index_to_id()
row_to_bizid = loader.get_id_to_bizid()


# ORDER: 'd_d_sim', 'd_d_w2vsim', 'd_t_sim', 'd_t_w2vsim', 't_d_sim', 't_d_w2vsim', 't_t_sim', 't_t_w2vsim', 'prior'
DEFAULT_WEIGHTS_DICT = OrderedDict([
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

DEFAULT_THRESHOLD = 0.0


class Featurizer:
    """
    Creates tf-idf and word2vec similarties for each text combination
    """

    def __init__(self):
        self.google_types = loader.get_business_types()
        self.model = loader.get_word2vecmodel()
        print "Loaded Models"

    def get_features(self, business, naics, ADD_SYNONYMS=False):
        """
        :param business: business dictionary from challenge set
        :param naics: list of naics dictionaries to check against
        :param ADD_SYNONYMS: boolean whether to add synonyms to titles and descriptions
        :return: dictionary of the 8 similarity combinations to their score
        """
        business_desc = business['description']
        google_type = self.google_types.get(business['unique_id'])
        business_name = business['name']
        if google_type:
            business_name += ' ' + google_type

        if ADD_SYNONYMS:
            business_desc = util.add_synonyms_to_text(business_desc)
            business_name = util.add_synonyms_to_text(business_name)
        else:
            business_desc = util.clean_paragraph(business_desc)
            business_name = util.clean_paragraph(business_name)

        codes_to_features = {}
        for naic in naics:
            naic_desc = naic['description']
            naic_title = naic['title']
            if ADD_SYNONYMS:
                naic_title = util.add_synonyms_to_text(naic_title)
                naic_desc = util.add_synonyms_to_text(naic_desc)
            else:
                naic_title = util.clean_paragraph(naic_title)
                naic_desc = util.clean_paragraph(naic_desc)

            d_d_sim = util.cosine_sim(business_desc, naic_desc)
            t_t_sim = util.cosine_sim(business_name, naic_title)
            d_t_sim = util.cosine_sim(business_desc, naic_title)
            t_d_sim = util.cosine_sim(business_name, naic_desc)

            t_t_w2vsim = util.word2vec_sim(business_name, naic_title, self.model)
            d_d_w2vsim = util.word2vec_sim(business_desc, naic_desc, self.model)
            d_t_w2vsim = util.word2vec_sim(business_desc, naic_title, self.model)
            t_d_w2vsim = util.word2vec_sim(business_name, naic_desc, self.model)

            t_t_w2vsim = util.removeNans(t_t_w2vsim)
            d_d_w2vsim = util.removeNans(d_d_w2vsim)
            d_t_w2vsim = util.removeNans(d_t_w2vsim)
            t_d_w2vsim = util.removeNans(t_d_w2vsim)

            features = {
                'd_d_sim': d_d_sim,
                't_t_sim': t_t_sim,
                'd_t_sim': d_t_sim,
                't_d_sim': t_d_sim,
                't_t_w2vsim': t_t_w2vsim,
                'd_d_w2vsim': d_d_w2vsim,
                'd_t_w2vsim': d_t_w2vsim,
                't_d_w2vsim': t_d_w2vsim
            }
            codes_to_features[naic['code']] = features
        return codes_to_features


class Classifier:
    """
    Classifies businesses to codes, assigns a unique code
    """

    # business attribute levels
    n = ['name']
    b = ['business_type']
    nb = ['name', 'business_type']
    nbd = ['name', 'business_type', 'description']

    # ids for rule based classification
    rule_words = [
        ('redbox', 532230, n),
        ('restaurant', 72251, nbd),
        ('veterinary', 541940, nbd),
        ('insurance', 524210, nb),
        ('dentist', 621210, nbd),
        ('dental', 621210, nbd),
        # ('physician', 621111, nbd),
        ('apartment', 531110, nbd),
        (' apt', 531110, nb),
        ('bank', 52, b),
        ('car_repair', 811111, nb),
        ('real_estate', 531210, nb),
        ('loan', 522310, nb),
        ('mortgage', 522310, nb),
        ('auto_repair', 811111, nb),
        # ('investment', 523930, nb),
        ('cemeter', 812220, nbd), # cemetary
        ('church', 813110, nb),
        ('florist', 453110, nbd),
        ('floral', 453110, nbd),
        ('car_wash', 811192, nb),
        ('landscap', 561730, nb),
        ('lawn', 561730, nb),
        ('laundromat', 812310, nbd),
        ('locksmith', 561622, nb),
        ('hotel', 721110, nb),
        ('motel', 721110, nb),
        ('photo', 541921, nb),
        ('gas', 447110, nb),
        # ('post_office', 491110, nbd),
        # ('jewelry', 448310, nbd)
    ]
    rule_based = []
    for word, code, attribute_list in rule_words:
        ids = ids_for_query(word, attribute_list)
        rule_based.append( (ids, code) )

    def __init__(self, weights_dict=DEFAULT_WEIGHTS_DICT, threshhold=DEFAULT_THRESHOLD):
        self.weights_dict = weights_dict
        self.threshhold = threshhold
        print "Threshhold", threshhold

    def classify(self, rule_based = True):
        classifications = []

        S = loader.get_S()
        S = [Si * wi for Si, wi in zip(S, self.weights_dict.values())]
        S = reduce(lambda x, y: x + y, S)

        for i in xrange(10000):
            bizid = row_to_bizid[i]
            code = self.ruleBasedClassification(bizid)
            if code is None or not rule_based:
                score = np.max(S[i, :])
                if score > self.threshhold:
                    code = column_to_code[np.argmax(S[i, :])]
                else:
                    code = ''  # no guess
            classifications.append( (row_to_bizid[i], code) )

        return classifications

    def ruleBasedClassification(self, bizid):
        for ids, code in self.rule_based:
            if bizid in ids:
                return code
        else:
            return None


class StochasticDescent:
    """
    Tries to find optimal weights through random weight pertubation.
    """

    def __init__(self, weights_dict=DEFAULT_WEIGHTS_DICT):
        self.weights_dict = weights_dict
        self.run()

    def run(self):
        S = loader.get_S()
        scorer = Scorer()

        for _ in xrange(10000):
            keys = self.weights_dict.keys()
            shuffle(keys)
            for k in keys:

                sc = -float("inf")
                best_dev = .02
                base = self.weights_dict[k]
                for dev in [.02, 0, -.02]:
                    self.weights_dict[k] = base + dev

                    w = self.weights_dict.values()

                    S_prime = [Si * wi for Si, wi in zip(S, w)]
                    S_prime = reduce(lambda x, y: x + y, S_prime)
                    classifications = []
                    for i in xrange(10000):
                        argmax = np.argmax(S_prime[i, :])
                        ide = column_to_code[argmax]
                        classifications.append( (row_to_bizid[i], ide) )
                    loader.write_rows_algo_classified_set(classifications)
                    pred , total , _  = scorer.scoreClassifications()
                    score = pred / total
                    if score > sc:
                        sc = score
                        best_dev = dev
                    print sc

                self.weights_dict[k] = base + best_dev
                w = self.weights_dict.values()

                S_prime = [Si * wi for Si, wi in zip(S, w)]
                S_prime = reduce(lambda x, y: x + y, S)
                classifications = []
                for i in xrange(10000):
                    ide = column_to_code[np.argmax(S_prime[i, :])]
                    classifications.append( (row_to_bizid[i], ide) )
                loader.write_rows_algo_classified_set(classifications)
                pred , total , _ = scorer.scoreClassifications()
                score = pred / total
                if score > sc:
                    sc = score
                    best_dev = dev
                print sc
                print self.weights_dict


class Scorer:
    """
    Scores classifications.
    """
    
    def __init__(self):
        self.hand_classified_set = loader.get_hand_classifiedset()
        self.algo_classified_set = loader.get_algo_classifiedset()


    def scoreClassifications(self):
        total = 0
        scores = []
        for uid, actual in self.hand_classified_set.iteritems():
            guess = self.algo_classified_set[uid]
            scores.append(util.score_prediction(guess, actual))
        total = sum(scores)
        max_potential = len(self.hand_classified_set.keys()) * 6.0
        unique, counts = np.unique(scores, return_counts=True)
        frequencies = np.asarray((unique, counts)).T

        return total, max_potential, frequencies
