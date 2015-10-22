import util
import loader
from collections import OrderedDict
import numpy as np
from classifier_site.dbHelper import ids_for_query
from random import shuffle


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

    # rule based classification
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
        if bizid in self.ids_with_redbox:
            return 532230
        elif bizid in self.ids_with_restaurant:
            return 72251
        elif bizid in self.ids_with_vet:
            return 541940
        elif bizid in self.ids_with_insurance:
            return 524210
        elif bizid in self.ids_with_dentist:
            return 621210
        elif bizid in self.ids_with_bank:
            return 52
        elif bizid in self.ids_with_car_repair:
            return 811111
        elif bizid in self.ids_with_landscaping:
            return 561730
        elif bizid in self.ids_with_locksmith:
            return 561622
        elif bizid in self.ids_with_hotel:
            return 721110
        elif bizid in self.ids_with_photo:
            return 541921
        else:
            return None


class StochasticDescent:


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
