#!/usr/bin/env python

"""
Script to get businesses types from their lat lon
"""

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import loader
import requests
import json
from util import cosine_sim

API_KEY = ""
# API_KEY = "AIzaSyDEVQJmING4SQSZbcap0YYV6Dt4dFt78tY" #Myles
# API_KEY = 'AIzaSyCdVPTYLYttmFGw7wVxNewCFV-DFSuUcBw' #Shane - don't use
# it too much it will charge my credit card
# API_KEY = "AIzaSyAKVlnW6xrtTdHtwnE1R2x-2ewJQb-ACCM"  # Shane
# API_KEY = "AIzaSyC43m3xgSQtkbFzQ5Oa8XMH3Gq49RCR3oU" #Alex
# API_KEY = "AIzaSyBYInlQYDWmJ3dGF7jGhl6_ArKcXHbdiyU" #Alex2


def get_places(lat, lng):
    uri = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%s,%s&radius=50&key=%s' % (
        lat, lng, API_KEY)
    resp = json.loads(requests.get(uri).content)
    if resp['status'] == 'OVER_QUERY_LIMIT':
        raise Exception('Over Query Limit')
    return resp['results']


def get_all_business_types():
    businesses = loader.get_challengeset()
    idtoloc = loader.get_idtoloc()
    business_types_dict = loader.get_business_types()
    print "Done {} of {}".format(len(business_types_dict), len(businesses))
    for business in businesses:
        unique_id = business['unique_id']
        if unique_id not in business_types_dict.keys():
            print business['name']
            closest_place, best_sim = None, 0
            lat, lon = idtoloc[unique_id]
            for place in get_places(lat, lon):
                sim = cosine_sim(place['name'], business['name'])
                if sim > best_sim:
                    closest_place = place
                    best_sim = sim
            if closest_place:
                types = filter(lambda x: not x in ['point_of_interest', 'establishment', 'sublocality', 'route',
                                                   'real', 'political', 'of', 'or', 'local', 'locality', 'intersection',
                                                   '1'], closest_place['types'])
                types = " ".join(types).replace("_", " ")
            else:
                types = None
            print types
            business_types_dict[unique_id] = types
            loader.dump_business_dict(business_types_dict)


if __name__ == '__main__':
    get_all_business_types()
