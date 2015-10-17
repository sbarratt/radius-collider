from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from flask import Flask, render_template, redirect, request, abort
from db import db
import dbHelper as dbh
import csv
import util
import loader

def create_app():
  app = Flask(__name__)
  app.config.from_object('config')
  app.jinja_env.add_extension('jinja2.ext.loopcontrols')
  db.init_app(app)
  with app.app_context():
    db.create_all()
  return app

app = create_app()

@app.route("/")
def root():
  return redirect('/classifier')

@app.route("/classifier")
def classifypage():
  guesses = []
  current_business = unclassified_businesses.pop()
  guesses = util.score_business(current_business, naics_items, ADD_SYNONYMS=True)
  code_list = util.bucket_guesses(guesses)
  business_type = business_types.get(current_business['unique_id'].encode())
  dbh.addBusiness(current_business, business_type, guesses, code_list)
  return render_template('classifypage.html', business=current_business, guesses=guesses,
      code_list=code_list, business_type=business_type)

@app.route('/c/<test>/<business_uid>/<naics_code>', methods=['POST'])
def classifyBusiness(test, business_uid, naics_code):
  if request.method == 'POST':
    with open('data/classified_set.csv', 'a') as classified_set:
      wr = csv.writer(classified_set)
      wr.writerow( ( business_uid, naics_code) )
    if test != 'test':
      with open('data/hand_classified_set.csv', 'a') as hand_classified_set_file:
        wr = csv.writer(hand_classified_set_file)
        wr.writerow( ( business_uid, naics_code) )
    return redirect('/classifier')
  else:
    return abort(405)  # 405 Method Not Allowed

@app.route('/database')
@app.route('/database/<int:page>', methods=['GET'])
def databaseView(page=1):
  businesses = dbh.getBusinessPage(page)
  return render_template('database.html', businesses=businesses,
      hand_classified_set=hand_classified_set, algo_classified_set=algo_classified_set)

if __name__ == "__main__":
  naics_items = loader.get_naics_data_for_level(6)
  hand_classified_set = loader.get_hand_classifiedset()
  algo_classified_set = loader.get_algo_classifiedset()
  unclassified_businesses = loader.get_unclassified_businesses()
  business_types = loader.get_business_types()
  app.run(debug=True)
