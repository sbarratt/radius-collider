import json # For loading the data

with open('../challenge_set.json') as data_file:
	businesses = json.load(data_file)