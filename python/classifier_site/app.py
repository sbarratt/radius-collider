#!/usr/bin/env python

"""
Run this file to run the flask server
"""

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from flask import Flask, render_template, redirect, request, abort
from db import db
import dbHelper as dbh
import loader
import util


def create_app():
    """
    creats a flask app with configs and connect db
    """
    app = Flask(__name__)
    app.config.from_object('config')
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    app.jinja_env.globals.update(get_score_color=util.get_score_color)
    app.jinja_env.globals.update(score_prediction=util.score_prediction)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app


app = create_app()


@app.route("/")
def root():
    return redirect('/agents')


@app.route("/classifier")
@app.route("/agents")
def agentspage():
    return render_template('agents.html')


@app.route("/classifier/<agent>")
def classifypage(agent):
    business = dbh.getNextUnclassifiedBusiness(unclassified_business_ids, agent)
    if business == None:
        abort(410)
    return render_template('classifypage.html', business=business, naics_dict=naics_dict, agent=agent)


@app.route('/c/<agent>/<test>/<business_uid>/<naics_code>', methods=['POST'])
def classifyBusiness(agent, test, business_uid, naics_code):
    if request.method == 'POST':
        loader.write_row_classified_set(business_uid, naics_code)
        if test != 'test':
            loader.write_row_hand_classified_set(business_uid, naics_code)
        return redirect('/classifier/' + agent)
    else:
        return abort(405)  # 405 Method Not Allowed


@app.route('/database')
@app.route('/database/<int:page>', methods=['GET'])
def databaseView(page=1):
    businesses = dbh.getBusinessPage(page)
    return render_template('database.html', businesses=businesses, hand_classified_set=hand_classified_set,
                           algo_classified_set=algo_classified_set, naics_dict=naics_dict)


if __name__ == "__main__":
    naics_items = loader.get_naics_data_for_level(6)
    hand_classified_set = loader.get_hand_classifiedset()
    algo_classified_set = loader.get_algo_classifiedset()
    unclassified_business_ids = loader.get_unclassified_business_ids()
    business_types = loader.get_business_types()
    naics_dict = loader.get_naics_dict()
    app.run(debug=True)
