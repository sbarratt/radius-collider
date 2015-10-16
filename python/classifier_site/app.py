if __name__ == '__main__' and __package__ is None:
  from os import sys, path
  sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
  from flask import Flask, render_template, redirect, request, abort
  import json
  import csv
  import util

app = Flask(__name__)

@app.route("/classify")
def classifypage():
  guesses = []
  current_business = unclassified_businesses.pop()
  guesses = util.score_business(current_business, naics_items, ADD_SYNONYMS=True)
  code_list = bucket_guesses(guesses)
  return render_template('classifypage.html', business=current_business, guesses=guesses, code_list=code_list)

@app.route('/c/<business_uid>/<naics_code>', methods=['POST'])
def classifyBusiness(business_uid, naics_code):
    if request.method == 'POST':
      with open('classified_set.csv', 'a') as classified_set:
        wr = csv.writer(classified_set)
        wr.writerow( ( business_uid, naics_code ) )
      return redirect('/classify')
    else:
        return abort(405)  # 405 Method Not Allowed

def get_unclassified_businesses():
  with open('challenge_set.json', 'r') as data_file:
    businesses = json.load(data_file)
    unclassified = []
    ids = get_classified_business_ids()
    for b in businesses:
      if b['unique_id'] not in ids:
        unclassified.append(b)
    return unclassified

def get_classified_business_ids():
  with open('classified_set.csv', 'r') as data_file:
    reader = csv.reader(data_file)
    ids = []
    for row in reader:
      ids.append(row[0])
    return ids

def get_naics_data_for_level(code_length):
  with open('naics_list.json', 'r') as jsonfile:
    naics_data = json.load(jsonfile)
  results = []
  for naics_item in naics_data:
    if len(str(naics_item['code'])) == code_length:
      results.append(naics_item)
  return results

def bucket_guesses(guesses, threshold=0):
  codes = {}
  for score, naic in guesses:
    if score > threshold:
      key = str(naic['code'])[:3]
      codes[key] = score + codes[key] if key in codes else score

  code_list = sorted(codes.items(), key=lambda x: x[1], reverse=True)
  return code_list

if __name__ == "__main__":
  naics_items = get_naics_data_for_level(6)
  unclassified_businesses = get_unclassified_businesses()
  app.run(debug=True)


# [
#   {
#     "website": [
#       "http://wolfleylawoffice.com",
#       "http://www.wolfleylawoffice.com",
#       "http://www.josephbwolfley.com"
#     ],
#     "description": "Equal...",
#     "address": "713 E 1ST ST, PORT ANGELES WA 98362",
#     "unique_id": "2112e3a5-1160-49c7-81e6-b27f9fad31a3",
#     "name": "Law Office of Lane J Wolfley"
#   }
# ]
