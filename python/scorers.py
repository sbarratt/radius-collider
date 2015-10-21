import bisect
import util
import loader
import numpy as np

DEFAULT_WIEGHTS_DICT = {
    'd_d_sim': .1,
    't_t_sim': .2,
    'd_t_sim': .1,
    't_d_sim': .1,
    't_t_w2vsim': .5,
    'd_d_w2vsim': .2,
    'd_t_w2vsim': .2,
    't_d_w2vsim': .2
}


class TfidfScorer:
    google_types = loader.get_business_types()
    model = loader.get_word2vecmodel()
    reuters_model = loader.get_word2vecmodel_reuters()
    print "Loaded Models"

    def __init__(self, weights_dict=DEFAULT_WIEGHTS_DICT):
        self.weights_dict = weights_dict

    @staticmethod
    def get_features(business, naics, ADD_SYNONYMS=False):
        """
        :param business: business dictionary from challenge set
        :param naics: list of naics dictionaries to check against
        :param ADD_SYNONYMS: boolean whether to add synonyms to titles and descriptions
        :return: dictionary of the 8 similarity combinations to their score
        """
        business_desc = business['description']
        google_type = TfidfScorer.google_types.get(business['unique_id'])
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

            t_t_w2vsim = word2vec_sim(business_name, naic_title)
            d_d_w2vsim = word2vec_sim(business_desc, naic_desc)
            d_t_w2vsim = word2vec_sim(business_desc, naic_title)
            t_d_w2vsim = word2vec_sim(business_name, naic_desc)

            t_t_w2vsim = removeNans(t_t_w2vsim)
            d_d_w2vsim = removeNans(d_d_w2vsim)
            d_t_w2vsim = removeNans(d_t_w2vsim)
            t_d_w2vsim = removeNans(t_d_w2vsim)

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

    def score_business(self, business_from_db):
        """
        :param business_from_db: business from the database
        :return: the sum of each feature multiplied by its weight
        """
        l = []
        for naics_code, features in business_from_db.getFeatureDict().iteritems():
            score = sum([self.weights_dict[k] * features[k] for k in features.keys()])
            bisect.insort(l, (score, naics_code))
        return l[::-1]


def removeNans(var):
    """
    prune NANs
    """
    if type(var) is not np.float64 or np.isnan(var):
        var = 0.0
    return float(var)


def word2vec_sim(text1, text2):
    w1 = filter(lambda x: x in TfidfScorer.model.vocab,
                util.clean_paragraph(text1))
    w2 = filter(lambda x: x in TfidfScorer.model.vocab,
                util.clean_paragraph(text2))
    if not w1 or not w2:
        return .1  # default value
    return TfidfScorer.model.n_similarity(w1, w2)
