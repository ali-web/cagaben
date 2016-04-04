# Standard Core Python Libraries
import csv, json, os, sys
from time import time
from pprint import pprint

# MongoDB Python Interface
from pymongo import MongoClient

# SciKit Learn Libraries
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np


ADAScores = {
	'washtimes': 35.4, #1
	'FoxNews': 39.7, #2
	'cnn': 56.0, #4
	'usatoday': 63.4, #6
	'washingtonpost': 66.6, #8
	'latimes': 70.0, #9
	'CBSNews': 73.7, #10
	'nytimes': 73.7 #11
}

alignment = {
	'washtimes': 0,
	'FoxNews': 0,
	'cnn': 1,
	'usatoday': 1,
	'washingtonpost': 1,
	'latimes': 1,
	'CBSNews': 2,
	'nytimes': 2
}


def pull_mongo_data(db, col):

	# Connect to MongoDB
	cur = MongoClient()[db][col]

	# Query DB, looking for all sources to take inventory
	db_results = cur.find({}, { "source" : 1 } )

	# Gather unique topics
	all_sources = list(set([story["source"] for story in db_results]))

	stories = []
	for source in all_sources:

		# Query the DB for all results that match the given source
		db_results = cur.find({ "source" : source }).limit(180)
		# db_results = cur.find({ "source" : source })
		stories.extend(db_results)

	# Query the DB for all results
	return stories


def word_freq(stories):

	# Strip the content out of the database entries, as
	# the TF-IDF algorithm only likes documents
	documents = []
	for story in stories:
		documents.append(story["content"])
	num_stories = len(documents)

	# Scikit Learn TF-IDF syntax
	vectorizer = TfidfVectorizer(
		encoding='latin1', 
		stop_words='english',
		max_features=2000,
		use_idf=False,
		norm=False,
		binary=True
		)

	scipy_word_freq = vectorizer.fit_transform(documents)

	# Get the names of the features (words)
	f_names = vectorizer.get_feature_names()

	# Convert to Python List
	X_train = [np.array(story)[0].tolist() for story in scipy_word_freq.todense()]

	X_train = [[int(freq) for freq in story] for story in X_train]

	return X_train, f_names


def agencies(stories):

	source_lookup = {}
	y_train = []

	for story in stories:
		source = story["source"]
		if source not in source_lookup:
			source_lookup[source] = len(source_lookup)
		# y_train.append(source_lookup[source])
		# y_train.append(ADAScores[source])
		y_train.append(alignment[source])

	return y_train


def write_to_csv(X_train, y_train, f_names):

	with open('story_400_500_ada_binary.csv', 'wb') as csvfile:
		wr = csv.writer(
			csvfile, 
			delimiter=',', 
			quoting=csv.QUOTE_MINIMAL)

		# First row is feature names
		row1 = [f.encode('utf8') for f in f_names]
		row1.append("y_value")
		wr.writerow(row1)

		for r in range(len(X_train)):
			X_train[r].append(y_train[r])
			wr.writerow(X_train[r])



if __name__ == "__main__":

	t0 = time()

	# Grab all data from Mongo
	db_results = pull_mongo_data("news_bias", "story")

	# Add word frequencies to data
	X_train, f_names = word_freq(db_results)

	# Grab assignments
	y_train = agencies(db_results)

	# print X_train
	print len(X_train[0])

	# Write to CSV
	write_to_csv(X_train, y_train, f_names)



	print("--- %s seconds ---" % (time() - t0))
