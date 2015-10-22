#!/usr/bin/env python

"""
Database Models.
"""

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from db import db
import util
import bisect

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

class Business(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(80))
    name = db.Column(db.String(80))
    address = db.Column(db.String(80))
    description = db.Column(db.Text)
    website = db.Column(db.String(40))
    business_type = db.Column(db.String(40))
    features_dict = db.Column(db.PickleType)  # dictionary of NAICS codes to features

    def __init__(self, business, business_type, features_dict):
        self.unique_id = business['unique_id']
        self.name = business['name']
        self.address = business['address']
        self.description = business['description']
        self.website = business['website'][0] if business['website'] else None
        self.business_type = business_type
        self.features_dict = features_dict

    def getSixCodeGuesses(self):
        """
        :return: the sum of each feature multiplied by its weight
        """
        l = []
        for naics_code, features in self.features_dict.iteritems():
            score = sum([DEFAULT_WIEGHTS_DICT[k] * features[k] for k in features.keys()])
            bisect.insort(l, (score, naics_code))
        return l[::-1]

    def getThreeCodeBuckets(self):
        return util.bucket_guesses(self.getSixCodeGuesses())

    def getFeatureDict(self):
        return self.features_dict

    def __repr__(self):
        return '<Business %r>' % self.name
