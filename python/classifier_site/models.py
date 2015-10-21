from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from db import db
import util
from scorers import TfidfScorer


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
        return TfidfScorer().score_business(self)

    def getThreeCodeBuckets(self):
        return util.bucket_guesses(self.getSixCodeGuesses())

    def getFeatureDict(self):
        return self.features_dict

    def __repr__(self):
        return '<Business %r>' % self.name
