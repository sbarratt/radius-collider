"""
python/get_business_latlon.py

Script to get businesses lat and lon and write to a pickle file
"""
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import loader
import requests
import json
import pickle


class GoogleGeocodingApi:
    def __init__(self):
        # self.api_key = 'AIzaSyAQOpIyo2L-6SpL3e5lylN-dnahV9MPC5I'
        # self.api_key = 'AIzaSyAyfNXRsPPrp01iWz7EA2xmxge7NcUELxY'
        raise Exception("No api key")

    def decode_address(self, address):
        """
        :param address: string
        :return: lat, lon (int)
        """
        uri = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s' % (address, self.api_key)
        resp = json.loads(requests.get(uri).content)
        try:
            temp = resp['results'][0]['geometry']['location']
            return temp['lat'], temp['lng']
        except:
            return None, None


def get_business_lat_lon():
    gapi = GoogleGeocodingApi()
    id_to_loc = loader.get_idtoloc()
    businesses = loader.get_challengeset()
    for business in businesses:
        unique_id = business['unique_id']
        address = business['address']
        if id_to_loc.get(unique_id) is None:
            print business['name']
            lat, lng = gapi.decode_address(address)
            id_to_loc[unique_id] = (lat, lng)
        pickle.dump(id_to_loc, open('../../data/id_to_loc.pickle', 'w'))


if __name__ == '__main__':
    get_business_lat_lon()
