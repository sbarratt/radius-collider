#!/usr/bin/env python

"""
Merge hand classifications
"""

import csv, os

DATA_DIR = os.path.dirname(os.path.dirname(
    os.path.realpath(__file__))) + "/../data/"

file1 = "hand_classified_set_alex.csv"
file2 = "hand_classified_set_shane.csv"
outputfile = "hand_classified_set.csv"

dict1 = {}
dict2 = {}

ct_duplicates = 0
with open(DATA_DIR + file1, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        if dict1.get(row[0]):
            ct_duplicates = ct_duplicates + 1
        dict1[row[0]] = int(row[1])

print file1, "duplicates:", ct_duplicates

ct_duplicates = 0
with open(DATA_DIR + file2, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        if dict2.get(row[0]):
            ct_duplicates = ct_duplicates + 1
        dict2[row[0]] = int(row[1])

print file2, "duplicates:", ct_duplicates

finaldict = dict1.copy()
finaldict.update(dict2)


print len(dict1.keys())
print len(dict2.keys())
print len(finaldict.keys())

with open(DATA_DIR + outputfile, 'w+') as hand_classified_set_file:
    wr = csv.writer(hand_classified_set_file)
    for k,v in finaldict.iteritems():
        wr.writerow((k, v))

