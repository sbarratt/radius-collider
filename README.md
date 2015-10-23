# Business NAICS Classifier

Codebase for [Radius Collider Project](http://cet.berkeley.edu/radius-fall-2015/).

Link to [Github repository](https://github.com/sbarratt/radius-collider).

The NAICS Classifier consists of an **assisted classifier** and a **database viewer** to see the scores assigned to each business, as well as a CLI to score each business and assign it a NAICS code.

## Downloading the classification matrices

Download *.npy under classification/ from [here](goo.gl/Sei2jU)

## Running the server
```bash
git clone <REPO>
cd radius-collider/python
sudo pip install -r ./requirements.txt
python
>>> nltk.download()
>>> quit()
python classifier_site/app.py
```

## Endpoints
`/agents`:

Page to choose your who you are classifying under.

`/classifier/<agent_name>`:
    
Assisted classifier to ease the painful process of hand-classification. Displays information about the business to be classified and a list of NAICS codes sorted by a preliminary algorithm's scoring function.

![Alt text](tex/handclassifier.png?raw=true "Assisted Classifier")


`/database`

Helps understand the structure of the data and the quality of the classifier. Reads the hand-classification and algorithm-classification databases. Displays a table of businesses with our hand-classification and algorithm-classification to discern what is wrong and why.

![Alt text](tex/database.png?raw=true "Database")

## CLI (command line interface)
```bash
python cli.py <METHOD>
```
Methods: 
- `initdb`: Initiliaze the Database
- `dropdb`: Drop the Database
- `restartDb`: Drop then initialize the Database
- `loadBusinesses`: Loads all businesses into the DB
    + *chunk*: choose the chunk of all businesses [0, 1, 2]
    + *processes*: specify number of processes to use
- `classifyBusinessWithScorer`: classifies businesses to a unique NAICS code naively
- `predictionScoreOfTrainingSet`: Scores the alogrithm's prediction


## Tree
```
.
├── README.md
├── data
│   ├── NAICS_descriptions.csv
│   ├── algo_classified_set.csv
│   ├── brown_model*
│   ├── business_types.pickle
│   ├── challenge_set.json
│   ├── classification
│   │   ├── id_to_bizid.pickle
│   │   ├── id_to_index.pickle
│   │   ├── index_to_id.pickle
│   │   ├── s0.npy*
│   │   ├── s1.npy*
│   │   ├── s2.npy*
│   │   ├── s3.npy*
│   │   ├── s4.npy*
│   │   ├── s5.npy*
│   │   ├── s6.npy*
│   │   └── s7.npy*
│   ├── classified_set.csv
│   ├── hand_classified_set.csv
│   ├── id_to_loc.pickle
│   ├── industry_counts.csv
│   ├── naics.json
│   ├── naics_list.json
│   ├── reuters_model*
│   └── word2vec_model*
├── python
│   ├── __init__.py
│   ├── classifier_site
│   │   ├── __init__.py
│   │   ├── __init__.pyc
│   │   ├── app.db*
│   │   ├── app.py
│   │   ├── cli.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── dbHelper.py
│   │   ├── models.py
│   │   ├── static
│   │   │   ├── css
│   │   │   │   ├── bootstrap-theme.css
│   │   │   │   ├── bootstrap-theme.css.map
│   │   │   │   ├── bootstrap-theme.min.css
│   │   │   │   ├── bootstrap.css
│   │   │   │   ├── bootstrap.css.map
│   │   │   │   ├── bootstrap.min.css
│   │   │   │   └── extra.css
│   │   │   ├── fonts
│   │   │   └── js
│   │   │       └── bootstrap.min.js
│   │   └── templates
│   │       ├── agents.html
│   │       ├── classifypage.html
│   │       └── database.html
│   ├── examples
│   │   ├── tf_idf_example.py
│   │   └── wordnet_example.py
│   ├── loader.py
│   ├── requirements.txt
│   ├── scorers.py
│   ├── scripts
│   │   ├── __init__.py
│   │   ├── clean_business_types.py
│   │   ├── dbs
│   │   │   └── *
│   │   ├── generate_matrices.py
│   │   ├── get_business_latlon.py
│   │   ├── get_business_types.py
│   │   ├── get_naics_data.py
│   │   └── merge_dbs.py
│   └── util.py
└── tex
    ├── database.png
    ├── handclassifier.png
    └── writeup.tex
```