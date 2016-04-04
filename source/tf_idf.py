# Standard Core Python Libraries
import os, sys, json
from time import time
from pprint import pprint

# MongoDB Python Interface
from pymongo import MongoClient

# Datamining Libraries
from sklearn import linear_model, metrics
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.neural_network import BernoulliRBM
from sklearn.pipeline import Pipeline
from sklearn import svm

import scipy.sparse as sp
import numpy as np
import pickle

ADAScores = {
    'washtimes': 35.4, #1
    'FoxNews': 39.7, #2

    #'NewsHour', #3
    'cnn': 56.0, #4
    # 'gma': 56.1, #5
    'usatoday': 63.4, #6
    #'usnews', #7
    'washingtonpost': 66.6, #8
    'latimes': 70.0, #9

    'CBSNews': 73.7, #10
    'nytimes': 73.7, #11
    #'wsj', #12 - not good
}

political_alignments = [
    ("Conservative", [
        "washtimes",
        "FoxNews"]),
    ("Neutral", [
        "cnn",
        "usatoday",
        "washingtonpost"],
     "latimes"),
    ("Liberal", [
        "CBSNews",
        "nytimes"])
]

pol_align_lookup = {
    "washtimes" : 0,
    "FoxNews" : 0,
    # "cnn" : 1,
    "usatoday" : 1,
    "washingtonpost" : 1,
    # "latimes" : 1,
    "CBSNews" : 2,
    "nytimes" : 2
}

# pol_align_lookup = {
# 	"washtimes" : 0,
# 	"FoxNews" : 0,
# 	"cnn" : 0,
# 	"usatoday" : 0,
# 	"washingtonpost" : 1,
# 	"latimes" : 1,
# 	"CBSNews" : 1,
# 	"nytimes" : 1
# }

freq_threshold = 0.1


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

def tf_idf(stories):

    # Strip the content out of the database entries, as
    # the TF-IDF algorithm only likes documents
    documents = []
    for story in stories:
        documents.append(story["content"])

    # Scikit Learn TF-IDF syntax
    vectorizer = TfidfVectorizer(encoding='latin1', stop_words='english')
    X_train = vectorizer.fit_transform(documents)

    # Use NGRAMs instead
    # vectorizer = CountVectorizer(stop_words='english',
    # 						max_df=0.95,
    # 						min_df=0.05,
    # 						analyzer='char',
    # 						ngram_range = [2,5], binary=True)
    # X_train = vectorizer.fit_transform(documents)

    # Get the names of the features (words)
    feature_names = vectorizer.get_feature_names()

    # Final result to return
    all_tfs = []

    for doc in X_train:

        # convert the sparse matrix to a Python list
        doc = doc.todense()
        doc = np.array(doc)[0].tolist()

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

    # Filter the results down to some frequency threshold
    all_tfs = filter_results(all_tfs)

    # Attach TF scores to the stories
    for i in range(len(stories)):
        stories[i]["tf"] = all_tfs[i]

    return stories


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

    # IDF is all stories in the collection
    if idf_group == "ALL":

        # Query the DB for all results
        db_results = collection.find()

        # Call the tf_idf function to compute given the current selection
        tf.append(tf_idf([item for item in db_results]))

    # IDF is all stories under the same Topic
    elif idf_group == "A":

        # Query DB, looking for all topics to take inventory
        db_results = collection.find({}, { "topic" : 1 } )

        # Gather unique topics
        all_topics = list(set(list(story["topic"] for story in db_results)))

        for topic in all_topics:

            # Query the DB for all results that match the given topic
            db_results = collection.find({ "topic" : topic })

            # Call the tf_idf function to compute given the current selection
            tf.append(tf_idf([item for item in db_results]))

    # IDF is all stories under the same political alignment
    elif idf_group == "B":

        # Populate with queries
        queries = []
        for alignment in political_alignments:

            # Create the general query
            query = { "source" : { "$in": [] } }

            # Put the agencies into the query
            query["source"]["$in"] = alignment[1]

            # Add the query to the list of queries
            queries.append(query)

        # Query the database for the different alignments
        for alignment_query in queries:

            # Query the DB for all results that match the given source
            db_results = collection.find(alignment_query)

            tf.append(tf_idf([item for item in db_results]))

    # IDF is all stories under the same Agency
    elif idf_group == "C":

        # Query DB, looking for all sources to take inventory
        db_results = collection.find({}, { "source" : 1 } )

        # Gather unique sources
        all_sources = list(set(list(story["source"] for story in db_results)))

        for source in all_sources:

            # Query the DB for all results that match the given source
            db_results = collection.find({ "source" : source })

            tf.append(tf_idf([item for item in db_results]))

    # IDF is all stories under the same Agency and Topic
    elif idf_group == "D":

        # Query DB, looking for all topics to take inventory
        db_results1 = collection.find({}, { "topic" : 1 } )
        # Query DB, looking for all sources to take inventory
        db_results2 = collection.find({}, { "source" : 1 } )

        # Gather unique topics
        all_topics = list(set(list(story["topic"] for story in db_results1)))
        # Gather unique sources
        all_sources = list(set(list(story["source"] for story in db_results2)))

        for topic in all_topics:

            for source in all_sources:

                # Query the DB for all results that match the given source
                db_results = collection.find({ "topic" : topic, "source" : source })

                tf.append(tf_idf([item for item in db_results]))

    else:
        print ("The selection: " + str(idf_group) + " is not valid")
        sys.exit()

    # Flatten the list of lists before returning
    return [item for sublist in tf for item in sublist]


def filter_results(tf_stories):

    result = []

    for story in tf_stories:

        # Add an empy list to append these words to
        result.append([])

        for tf in story:

            # If we have gone below the threshold, stop adding words from that story
            if tf[1] < freq_threshold:
                break

            # We are still within our threshold, add words
            result[-1].append(tf)

    return result

def format_data(tf_stories):
    global all_words

    X = []
    y = []

    # Only do this once, for the train set
    if len(all_words) == 0:
        # Create list of all words found
        for story in tf_stories:

            #TESTING CODE TO SKIP SOURCES NOT INCLUDED
            if story["source"] not in pol_align_lookup:
                continue

            for tf in story["tf"]:
                if tf[0] not in all_words:
                    all_words.append(tf[0])

        all_words = sorted(all_words)
    n_all_words = len(all_words)

    print n_all_words

    # Populate X where each row is a story
    for story in tf_stories:

        #TESTING CODE TO SKIP SOURCES NOT INCLUDED
        if story["source"] not in pol_align_lookup:
            continue

        # Assign value to y
        if model == "linear":
            y.append(ADAScores[story["source"]])
        elif model == "logistic":
            y.append(pol_align_lookup[story["source"]])

        X.append([0 for i in range(n_all_words)])

        for tf in story["tf"]:

            try: # Because the word may not be in 'all_words'

                if binary_feed:
                    # Populate X with binary existence of words
                    if tf[1] == 0:
                        X[-1][all_words.index(tf[0])] = 0
                    else:
                        X[-1][all_words.index(tf[0])] = 1
                else:
                    # Populate X with frequency at the index of words
                    X[-1][all_words.index(tf[0])] = tf[1]

                # OTHER METHODS OF POPULATING X


            except:
                continue

    return np.array(X), np.array(y)

if __name__ == "__main__":
    global all_words
    global model
    global binary_feed

    # If you DO NOT have the MongoDB on your machine, this HAS TO BE set to False
    database_exists = True
    if (database_exists):
        # col = connect_mongodb("cagaben7", "story")
        col = connect_mongodb("news_bias", "story")

        tf_results = [[] for i in range(5)]

        tf_results[0] = tf_idf_selector("ALL", col)
        # tf_results[1] = tf_idf_selector("A", col)
        # tf_results[2] = tf_idf_selector("B", col)
        # tf_results[3] = tf_idf_selector("C", col)
        # tf_results[4] = tf_idf_selector("D", col)

        # save the tf_results
        with open('./program_data/tf_results.pkl', 'wb') as fid:
            pickle.dump(tf_results, fid)

    else:
        # load the tf_results
        with open('./program_data/tf_results.pkl', 'rb') as fid:
            tf_results = pickle.load(fid)

    # Pick which tf_results you wish to use:
    word_frequencies = tf_results[0]
    binary_feed = True


    # Cross validation - run against each agency separately
    for agency, alignment in pol_align_lookup.iteritems():
        print
        print agency

        # Split the data into Train and Test
        train_set = []
        test_set = []
        for story in word_frequencies:
            # if story["topic"] != "gun control":
            # 	continue

            if story["source"] == agency:
                test_set.append(story)
            else:
                train_set.append(story)

            # BAD DATA MINING
            # if story["source"] == agency:
            # 	test_set.append(story)
            # train_set.append(story)

        # TESTING
        # X_train, y_train = ([[5, 5], [6, 6], [7, 7], [8, 8]], [5, 6, 7, 8])
        # X_test, y_test = ([[5, 5], [6, 6], [7, 7], [8, 8]], [5, 6, 7, 8])



        # print X_train
        # print y_train
        # print X_test
        # print y_test
        # END TESTING

        # LOGISTIC MODEL
        # model = "logistic"

        # Format the train and test sets into X and y
        # all_words = []  # Clear all_words to be re-set
        # X_train, y_train = format_data(train_set)
        # X_test, y_test = format_data(test_set)

        # logistic = linear_model.LogisticRegression(
        # 	# solver="newton-cg",
        # 	solver="sag",
        # 	# solver="liblinear",
        # 	penalty="l2",
        # 	C=4000
        # 	# multi_class="multinomial"
        # 	)
        # logistic_regres = logistic.fit(X_train, y_train)
        # print logistic.coef_
        # print('LogisticRegression score: %f'
        # 	% logistic.fit(X_train, y_train).score(X_test, y_test))
        # print('Logistic score: %f' % logistic_regres.score(X_test, y_test))
        # print "Actual:    " + str(y_test)
        # print "Predicted: " + str(logistic_regres.predict(X_test))
        # END LOGISTIC MODEL

        # NAIVE BAYES

        # model = "logistic"

        # all_words = []  # Clear all_words to be re-set
        # X_train, y_train = format_data(train_set)
        # X_test, y_test = format_data(test_set)

        # # gnb = GaussianNB()
        # mnb = MultinomialNB()
        # y_pred = mnb.fit(X_train, y_train).predict(X_test)

        # print "Actual:    " + str(y_test)
        # print "Predicted: " + str(y_pred)

        # END NAIVE BAYES

        # SVM

        model = "logistic"

        all_words = []  # Clear all_words to be re-set
        X_train, y_train = format_data(train_set)
        X_test, y_test = format_data(test_set)

        clf = svm.SVC()
        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)

        print "Actual:    " + str(y_test)
        print "Predicted: " + str(y_pred)



    # END SVM

    # UNSUPERVISED NEURAL NETWORK

    # all_words = []  # Clear all_words to be re-set
    # X_train, y_train = format_data(train_set)
    # X_test, y_test = format_data(test_set)

    # # Models we will use
    # logistic = linear_model.LogisticRegression()
    # rbm = BernoulliRBM(random_state=0, verbose=True)

    # # classifier = Pipeline(steps=[('rbm', rbm), ('logistic', logistic)])


    # rbm.learning_rate = 0.06
    # rbm.n_iter = 100000000

    # rbm.n_components = 100

    # rbm.fit(X_train)

    # # logistic.C = 6000.0

    # # Training RBM-Logistic Pipeline
    # # classifier.fit(X_train, y_train)

    # rbm.score_samples(X_train)


    # END NEURAL NETWORK
    # model = "linear"
    # all_words = []  # Clear all_words to be re-set
    # X_train, y_train = format_data(train_set)
    # X_test, y_test = format_data(test_set)

    # # Make the linear model

    # linear = linear_model.Lasso(alpha=5)
    # linear_regres = linear.fit(X_train, y_train)
    # print('Linear score: %f' % linear_regres.score(X_test, y_test))

    # # Predict against the test set
    # print y_test
    # print linear_regres.predict(X_test)

    # sys.exit()
