"""
python/get_business_types.py

Script to get bussines types from the address via Google Places
"""

import json
import requests
import csv
import IPython as ipy
from util import cosine_sim

import requests
import json

# if __name__ == '__main__':
#   gapi = GoogleApi()
#   print gapi.decode_address('2327 warring st')
 
# API_KEY = "AIzaSyDEVQJmING4SQSZbcap0YYV6Dt4dFt78tY" #Myles 
API_KEY = 'AIzaSyCdVPTYLYttmFGw7wVxNewCFV-DFSuUcBw' #Shane - don't use it too much it will charge my credit card

gapi = GoogleApi()

def url(code):
  return "http://api.naics.us/v0/q?year=2012&code={}".format(code)

def get_place_id(address):
  lat, lng = gapi.decode_address(address) #helps to base it off latitude and longitude then put in a radius
  # uri = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=%s&radius=500&key=%s' % (address, API_KEY)
  uri = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%s,%s&radius=50&key=%s' % (lat, lng, API_KEY)
  resp = json.loads(requests.get(uri).content)
  return resp['results'][0]['types']

def get_places(lat,lng):
  # uri = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=%s&radius=500&key=%s' % (address, API_KEY)
  uri = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%s,%s&radius=50&key=%s' % (lat, lng, API_KEY)
  resp = json.loads(requests.get(uri).content)
  return resp['results']

# UNNECCESSARY
# def get_place_type(address):
#   place_id = get_place_id(address)
#   uri = 'https://maps.googleapis.com/maps/api/place/details/json?placeid=%s&key=%s' % (place_id, API_KEY)
#   resp = json.loads(requests.get(uri).content)
#   res = resp.get('result')
#   return res.get('types') if res else None

def get_all_business_types():
  with open('../../challenge_set.json') as data_file:
    businesses = json.load(data_file)
    for business in businesses:
      print business['name']
      # types = get_place_type(business['address'])
      closest_place, best_sim = None, 0
      for place in get_places(business['address']):
        sim = cosine_sim(place['name'], business['name'])
        if sim > best_sim:
          closest_place = place
          best_sim = sim
      if closest_place:
        types = filter(lambda x: not x in ['point_of_interest','establishment'], closest_place['types'])
        types = map(lambda x: x.replace("_"," "), types)
        types = " ".join(types)
      else:
        types = None
      print types
      with open('../../businesses_types.csv', 'a') as businesses_types:
        wr = csv.writer(businesses_types)
        wr.writerow( ( business['unique_id'],  ) )

if __name__ == '__main__':
  get_all_business_types()
  # print get_place_type('Law Office of Lane J Wolfley')
