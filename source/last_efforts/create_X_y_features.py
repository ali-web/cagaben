# Standard Core Python Libraries
import csv, json, os, sys
from time import time
from pprint import pprint

# MongoDB Python Interface
from pymongo import MongoClient

# SciKit Learn Libraries
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cross_validation import train_test_split
from sklearn import svm

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

alignment_6 = {
	'washtimes': ("Conservative", 0),
	'FoxNews': ("Conservative", 0),
	# 'cnn': ("Neutral", 1),
	'usatoday': ("Neutral", 1),
	'washingtonpost': ("Neutral", 1),
	# 'latimes': ("Neutral", 1),
	'CBSNews': ("Liberal", 2),
	'nytimes': ("Liberal", 2)
}

alignment_8 = {
	'washtimes': ("Conservative", 0),
	'FoxNews': ("Conservative", 0),
	'cnn': ("Neutral", 1),
	'usatoday': ("Neutral", 1),
	'washingtonpost': ("Neutral", 1),
	'latimes': ("Neutral", 1),
	'CBSNews': ("Liberal", 2),
	'nytimes': ("Liberal", 2)
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
		db_results = cur.find({ "source" : source }).limit(stories_per_agency)
		print source + " " + str(db_results.count())
		stories.extend(db_results)

	# Filter results based on alignment if using 'aln_6'
	if (predict == "aln6"):
		stories = [story for story in stories if story["source"] in alignment_6]


	# Grab unique links
	# print len(stories)
	# unique = list(set([(story['link'], story['source']) for story in stories]))

	# agency = "washingtonpost"
	# print agency + ": " + str(len([story[1] for story in unique if story[1] == agency]))

	return stories


def word_freq(stories):

	# Strip the content out of the database entries, as
	# the TF-IDF algorithm only likes documents
	documents = []
	for story in stories:
		documents.append(story["content"])

	# Scikit Learn TF-IDF syntax
	if (feature_type == "bool"):
		vectorizer = TfidfVectorizer(
			encoding='latin1', 
			stop_words='english',
			max_features=n_features,
			use_idf=False,
			norm=False,
			binary=True
			)
	elif (feature_type == "real"):
		vectorizer = TfidfVectorizer(
			encoding='latin1', 
			stop_words='english',
			max_features=n_features,
			)

	scipy_word_freq = vectorizer.fit_transform(documents)

	# Get the names of the features (words)
	f_names = vectorizer.get_feature_names()

	# Convert to Python List
	X_train = [np.array(story)[0].tolist() for story in scipy_word_freq.todense()]

	X_train = [[int(freq) for freq in story] for story in X_train]

	return X_train, f_names


def agencies(stories):

	y_train = []

	if (predict == "src"):
		source_lookup = {}
		for story in stories:
			source = story["source"]
			if source not in source_lookup:
				source_lookup[source] = len(source_lookup)
			y_train.append((source, source_lookup[source])[predict_type])
		# print source_lookup

	elif (predict == "ada"):
		for story in stories:
			y_train.append(ADAScores[story["source"]])

	elif (predict == "aln6"):
		for story in stories:
			y_train.append(alignment_6[story["source"]][predict_type])

	elif (predict == "aln8"):
		for story in stories:
			y_train.append(alignment_8[story["source"]][predict_type])

	return y_train


def write_to_csv(X_train, y_train, f_names):

	# When printing, the letters mean the following:
	# x: The type of feature we are using: bool or real
	# y: The category of class we are using
	# s: How many stories are in the dataset
	# f: How many features are in the dataset

	if not os.path.exists(folder_name):
		os.makedirs(folder_name)

	file_name = \
		folder_name + "/" + \
		"x_" + feature_type + \
		"__y_" + predict + \
		"__s_" + str(len(X_train)) + \
		"__f_" + str(len(X_train[0])) + ".csv"

	with open(file_name, 'wb') as csvfile:
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


def create_X_y(db, col):

	# Grab all data from Mongo
	db_results = pull_mongo_data(db, col)

	# Add word frequencies to data
	X, f_names = word_freq(db_results)

	# Grab assignments
	y = agencies(db_results)

	return X, y, f_names


def train_test_model(X, y, model):

	X_train, X_test, y_train, y_test = \
		train_test_split(X, y, test_size=0.2)

	if (model == "svc"):

		clf = svm.LinearSVC()
		clf.fit(X_train, y_train)

		print clf.score(X_test, y_test)

		# print "Actual:    " + str(y_test)
		# print "Predicted: " + str(y_pred)


if __name__ == "__main__":

	global stories_per_agency, predict, feature_type, n_features, folder_name

	# Change this if you want to write to a new folder
	folder_name = "new_with_strings"

	# Predict type 0 is a string, 1 is a number, e.g.
	# ("Conservative", 0)
	# Libraries like SciKitLearn require numbers (categories) isntead
	# of Strings, so I made this option. RapidMiner allows strings,
	# which increases readibility and auto-categorization as polynomial
	predict_type = [0, 1][1]


	##### Create One CSV #####
	t0 = time()

	# Up to this number, database may not have enough.
	stories_per_agency = [100, 200, 1000][-1]

	# Number of features to include
	n_features = [2000, 10000, 20000, 100000][0]

	# What attribute to predict
	predict = ["src", "ada", "aln6", "aln8"][0]

	# Should the X matrix contain binary features or not
	feature_type = ["bool", "real"][0]

	# Create the actual model and write to CSV
	X, y, f_names = create_X_y("news_bias", "story")

	# Write to CSV
	# write_to_csv(X, y, f_names)

	# Train and test the model
	train_test_model(X, y, "svc")

	t0 = time()
	##### END Create One CSV #####


	# These loops are to create CSVs for all possible options.
	# If you wish to create less CSVs (or just one), use the
	# following syntax:
	# for predict in ["src", "aln6", "aln8", "ada"][0:1]:
	# Notice the [0:] on the end? That will restrict to just the first 
	# item in the list. User [:2] for the first two items, etc.

	# for stories_per_agency in [100, 200, 1000][:]:
	# 	for n_features in [2000, 10000, 20000, 100000][:]:
	# 		for feature_type in ["bool", "real"][:1]:
	# 			for predict in ["src", "ada", "aln6", "aln8"][2:3]:

	# 				# Time the model creation
	# 				t0 = time()

	# 				# Display the current model being created
	# 				print "\nWorking on: " + \
	# 					feature_type + " " + \
	# 					predict + " " + \
	# 					str(stories_per_agency) + " " + \
	# 					str(n_features)

	# 				# Create the model and write to CSV
	# 				X, y, _ = create_X_y("news_bias", "story")

	# 					# Write to CSV
	# 				write_to_csv(X, y, f_names)

	# 				# Report model creation time
	# 				print("--- %s seconds ---" % (time() - t0))


	
