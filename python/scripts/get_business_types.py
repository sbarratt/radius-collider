"""
python/get_business_types.py

Script to get bussines types from the address via Google Places
"""

import json
import requests
import csv
import IPython as ipy

API_KEY = "AIzaSyDEVQJmING4SQSZbcap0YYV6Dt4dFt78tY"

def url(code):
  return "http://api.naics.us/v0/q?year=2012&code={}".format(code)

def get_place_id(address):
  uri = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=%s&key=%s' % (address, API_KEY)
  resp = json.loads(requests.get(uri).content)
  return resp['results'][0]['place_id']

def get_place_type(address):
  place_id = get_place_id(address)
  uri = 'https://maps.googleapis.com/maps/api/place/details/json?placeid=%s&key=%s' % (place_id, API_KEY)
  resp = json.loads(requests.get(uri).content)
  res = resp.get('result')
  return res.get('types') if res else None

def get_all_business_types():
  with open('../../challenge_set.json') as data_file:
    businesses = json.load(data_file)
    for business in businesses:
      print business['name']
      types = get_place_type(business['address'])
      if types:
        types = " ".join(types)
      else:
        types = None
      with open('../../businesses_types.csv', 'a') as businesses_types:
        wr = csv.writer(businesses_types)
        wr.writerow( ( business['unique_id'],  ) )

if __name__ == '__main__':
  get_all_business_types()
  # print get_place_type('Law Office of Lane J Wolfley')
