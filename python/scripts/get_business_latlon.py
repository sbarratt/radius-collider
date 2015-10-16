import requests
import json
import pickle
import IPython as ipy

class GoogleGeocodingApi:
  def __init__(self):
    # self.api_key = 'AIzaSyAQOpIyo2L-6SpL3e5lylN-dnahV9MPC5I' #we're kind of limited to 2,500 requests / day
    # self.api_key = 'AIzaSyAyfNXRsPPrp01iWz7EA2xmxge7NcUELxY'
    raise Exception("No api key")

  def decode_address(self, address):
    # Input: address (string)
    # Output: lat, lon (int)
    uri = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s' % (address, self.api_key)
    resp = json.loads(requests.get(uri).content)
    try:
      temp = resp['results'][0]['geometry']['location']
      return temp['lat'], temp['lng']
    except:
      return None, None

def get_business_lat_lon():
  gapi = GoogleGeocodingApi()
  id_to_loc = pickle.load(open('../../id_to_loc.pickle','r'))
  with open('../../challenge_set.json') as data_file:
    businesses = json.load(data_file)
    for business in businesses:
      unique_id = business['unique_id']
      address = business['address']
      if id_to_loc.get(unique_id) is None:
        print business['name']
        lat, lng = gapi.decode_address(address)
        id_to_loc[unique_id] = (lat, lng)
      pickle.dump(id_to_loc, open('../../id_to_loc.pickle','w'))

if __name__ == '__main__':
  get_business_lat_lon()