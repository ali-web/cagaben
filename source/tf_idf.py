# Standard Core Python Libraries
import os, sys, json
from time import time
from pprint import pprint

# MongoDB Python Interface
from pymongo import MongoClient

# Datamining Libraries
from sklearn.feature_extraction.text import TfidfVectorizer
import scipy.sparse as sp
import numpy

# Global Variables


def read(path):
	print ("")
	errors = 0

	try:
		os.chdir(path)
	except e:
		raise e

	client = MongoClient()
	ibm_dataset = client.ibm_dataset
	related = ibm_dataset.related

	for jsonFileName in os.listdir(path):
 
		f = open(jsonFileName,"r")

		try:
			text = json.load(f)
		except:
			print (f.name)
			errors += 1
			continue

		try:
			related.insert_one(text)
		except e:
			print (f.name)
			errors += 1
	print (errors)

def connect_mongodb(db, col):

	# Grab the collection from the database we want
	col = MongoClient()[db][col]

	# Return the collection cursor, to be queried later
	return col

def tf_idf(documents):

	# Scikit Learn TF-IDF syntax
	vectorizer = TfidfVectorizer(encoding='latin1')
	X_train = vectorizer.fit_transform(documents)

	# Get the names of the features (words)
	feature_names = vectorizer.get_feature_names()

	# Final result to return
	all_tfs = []

	for doc in X_train:

		# convert the sparse matrix to a Python list
		doc = doc.todense()
		doc = numpy.array(doc)[0].tolist()

		# Create a list for this story, it will contain (word, frequency) pairs
		tf = []

		for i in range(len(doc)):
			if (doc[i] != 0):
				tf.append((feature_names[i], doc[i]))
				# print ('{0:14} ==> {1:10f}'.format(tf[-1][0], tf[-1][1]))

		# Sort the list by frequency, descending
		tf = sorted(tf, key=lambda freq: freq[1], reverse=True)

		# Append this document's tf to all the tfs
		all_tfs.append(tf)
	return all_tfs

def find_sort_data(value, collection):
	# tf is all of the text frequencies per story, against the defined idf_group
	tf = []

	# Query DB, looking for all topics to take inventory
	db_results = collection.find({}, { value : 1 } )

	# Gather unique topics
	all_topics = list(set(list(story[value] for story in db_results)))

	for topic in all_topics:
		# Query the DB for all results that match the given topic
		db_results = collection.find({ value : topic })

		# Strip the content out of the database entries, as 
		# the TF-IDF algorithm only likes documents
		documents = []
		for story in db_results:
			documents.append(story["content"])

		# Filter Stop words
		# TODO

		tf.append(tf_idf(documents))

	# Flatten the list of lists before returning
	return [item for sublist in tf for item in sublist]

"""
def tf_idf_selector(idf_group, collection)
	idf_group:	'A' - Topic
							'B' - Political Alignment
							'C' - Agency
							'D' - Agency & Topic
	collection: The MongoDB collection to which we will query
"""
def tf_idf_selector(idf_group, collection):

	# tf is all of the text frequencies per story, against the defined idf_group
	tf = []

	# IDF is all stories under the same Topic
	if idf_group == "A":
		return find_sort_data("topic", collection)

	# IDF is all stories under the same political alignment
	elif idf_group == "B":
		pass

	# IDF is all stories under the same Agency
	elif idf_group == "C":
		return find_sort_data("source", collection)

	# IDF is all stories under the same Agency and Topic
	elif idf_group == "D":
		pass
	else:
		print ("The selection: " + str(idf_group) + " is not valid")
		return

if __name__ == "__main__":

	col = connect_mongodb("news_bias", "stories")

	results = tf_idf_selector("A", col)
	# results = tf_idf_selector("B", col)
	# results = tf_idf_selector("C", col)
	# results = tf_idf_selector("D", col)

	pprint (results)
	print (len(results))





