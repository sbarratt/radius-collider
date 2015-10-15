from flask import Flask, render_template, redirect, request, abort
import json
import csv

app = Flask(__name__)

@app.route("/classify")
def classifypage():
  guesses = []
  current_business = unclassified_businesses.pop()
  for naics_item in naics_items:
    # score = get_score(naics_item, current_business)
    score = 1.5
    guess = (naics_item, score)
    guesses.append(guess)
  guesses = sorted(guesses, key=lambda x: x[1])
  return render_template('classifypage.html', business=current_business, guesses=guesses)

@app.route('/c/<business_uid>/<naics_code>', methods=['POST'])
def classifyBusiness(business_uid, naics_code):
    if request.method == 'POST':
      with open('../../classified_set.csv', 'a') as classified_set:
        wr = csv.writer(classified_set)
        wr.writerow( ( business_uid, naics_code ) )
      return redirect('/classify')
    else:
        return abort(405)  # 405 Method Not Allowed

def get_naics_data_for_level(code_length):
  with open('../../naics_list.json', 'r') as jsonfile:
    naics_data = json.load(jsonfile)
  results = []
  for naics_item in naics_data:
    if len(str(naics_item['code'])) == code_length:
      results.append(naics_item)
  return results

def get_unclassified_businesses():
  with open('../../challenge_set.json', 'r') as data_file:
    businesses = json.load(data_file)
    unclassified = []
    ids = get_classified_business_ids()
    for b in businesses:
      if b['unique_id'] not in ids:
        unclassified.append(b)
    return unclassified

def get_classified_business_ids():
  with open('../../classified_set.csv', 'r') as data_file:
    reader = csv.reader(data_file)
    ids = []
    for row in reader:
      ids.append(row[0])
    return ids

if __name__ == "__main__":
  naics_items = get_naics_data_for_level(2)
  unclassified_businesses = get_unclassified_businesses()
  app.run(debug=True)


# [
#   {
#     "website": [
#       "http://wolfleylawoffice.com",
#       "http://www.wolfleylawoffice.com",
#       "http://www.josephbwolfley.com"
#     ],
#     "description": "Equal Justice For All. At the Law Offices of Wolfley & Wolfley, P.S., in Port Angeles, WA, you will get aggressive legal representation in your personal injury or workers’ compensation case to help you get the compensation you deserve...",
#     "address": "713 E 1ST ST, PORT ANGELES WA 98362",
#     "unique_id": "2112e3a5-1160-49c7-81e6-b27f9fad31a3",
#     "name": "Law Office of Lane J Wolfley"
#   }
# ]
