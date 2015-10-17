# Business NAICS Classifier


## Running the server
```bash
cd radius-collider/python
pip install requirements.txt
python
>>> nltk.download()
>>> quit()
python classifier_site/app.py
```

## Views
`/classifier`:
    
Assisted hand classifier for businesses. Gives suggestions and score of possible classifications  
TODO: picture

`/database`

View of suggestions and scores of Businesses in the database, as well as the hand classified code and the algorithm classified code  
TODO: picture

## CLI (command line interface)
```bash
python classifier_site/cli.py <METHOD>
```
Methods: 
- `initdb`: Initiliaze the Database
- `dropdb`: Drop the Database
- `resetDB`: Drop then initialize the Database
- `loadAllBusinesses`: Loads all businesses along with their 6 code scores and 3 code buckets
- `classifyBusinessWithAlgo`: Loops through Businesses in the Database and classifies the Business based on some logic


## Datasources

`id_to_loc.pickle`: a dictionary of business unique_id to a tuple (lat, lon)

`naics_list.json`: a json list of NAICS objects with code, title, description

`hand_classified_set.csv`: a csv of hand classified businesses - unique_id,naics_code

`algo_classified_set.csv`: a csv of algorithm classified businesses - unique_id,naics_code

`business_types.pickle`: a dictionary of business unique_id to a string Type

`challenge_set.json`: a json list of business objects given from Radius to classify


## Scripts

`get_business_latlot.py`: generates *id_to_loc.pickle*

`get_business_types.py`: generates *business_types.pickle*

`get_naics_data.py`: generates *naics_list.json*


## TODO
- parrallize cli.py#loadAllBusinesses
- optimize scoring alogrithm
- create logic to choose code from score
- add all businesses to db
- classify 1000 by hand
- classify 10000 by algo
- comment code, and re-organize
- put output format (as in loader.py) into README#Datasources

