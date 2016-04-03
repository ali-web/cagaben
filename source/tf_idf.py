# Standard Core Python Libraries
import os, sys, json
from time import time
from pprint import pprint

# MongoDB Python Interface
from pymongo import MongoClient

# Datamining Libraries
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import linear_model
import scipy.sparse as sp
import numpy as np

ADAScores = {
    'washtimes': 35.4, #1
    'FoxNews': 39.7, #2

    #'NewsHour', #3
    'cnn': 56.0, #4
    'gma': 56.1, #5
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
        "washingtonpost"]),
    ("Liberal", [
        "latimes",
        "CBSNews",
        "nytimes"])
]

pol_align_lookup = {
    # "washtimes" : 0,
    "FoxNews" : 1,
    "cnn" : 2,
    # "usatoday" : 1,
    # "washingtonpost" : 1,
    # "latimes" : 1,
    # "CBSNews" : 2,
    # "nytimes" : 2
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

freq_threshold = 0.2


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

    # IDF is all stories under the same Topic
    if idf_group == "A":

        # Query DB, looking for all topics to take inventory
        db_results = collection.find({}, { "topic" : 1 } )

        # Gather unique topics
        all_topics = list(set(list(story["topic"] for story in db_results)))

        for topic in all_topics:

            # Query the DB for all results that match the given topic
            db_results = collection.find({ "topic" : topic })

            # Call the tf_idf function to compute given the current selection
            tf.append(tf_idf([item for item in db_results]))

        # Flatten the list of lists before returning
        return [item for sublist in tf for item in sublist]

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

        # Flatten the list of lists before returning
        return [item for sublist in tf for item in sublist]

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

        # Flatten the list of lists before returning
        return [item for sublist in tf for item in sublist]

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

        # Flatten the list of lists before returning
        return [item for sublist in tf for item in sublist]

    else:
        print ("The selection: " + str(idf_group) + " is not valid")
        return

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
            for tf in story["tf"]:
                if tf[0] not in all_words:
                    all_words.append(tf[0])

        all_words = sorted(all_words)
    n_all_words = len(all_words)

    # Populate X where each row is a story
    for story in tf_stories:

        # Assign value to y
        y.append(ADAScores[story["source"]])
        # y.append(pol_align_lookup[story["source"]])

        # JUST FOR TESTING
        # X.append([ADAScores[story["source"]]*10])
        # continue

        X.append([0 for i in range(n_all_words)])

        for tf in story["tf"]:

            try: # Because the word may not be in 'all_words'

                # Populate X with frequency at the index of words
                X[-1][all_words.index(tf[0])] = tf[1]

            # Populate X with binary existence of words
            # if tf[1] == 0:
            # 	X[-1][all_words.index(tf[0])] = 0
            # else:
            # 	X[-1][all_words.index(tf[0])] = 1

            # OTHER METHODS OF POPULATING X


            except:
                continue

    return np.array(X), np.array(y)

if __name__ == "__main__":
    global all_words

    col = connect_mongodb("cagaben9", "story")
    # col = connect_mongodb("cagaben_2_sources1", "story")
    # col = connect_mongodb("news_bias", "story")

    tf_results = tf_idf_selector("A", col)

    # for agency, alignment in pol_align_lookup.iteritems():
    #     print
    #     print agency

        # Split the data into Train and Test


    j = 0
    for i in range(0, 20):
        train_set = []
        test_set = []

        for story in tf_results:
            if story["topic"] != "gun control":
                continue

            if i == j:
                test_set.append(story)
            # if story["source"] == agency:
            #     test_set.append(story)
            else:
                train_set.append(story)

            j += 1



        # print len(train_set)
        # print len(test_set)

        # Format the train and test sets into X and y
        all_words = []  # Clear all_words to be re-set
        X_train, y_train = format_data(train_set)
        X_test, y_test = format_data(test_set)

        # TESTING
        # X_train, y_train = ([[5], [6], [7], [8]], [5, 6, 7, 8])
        # X_test, y_test = ([[5], [6], [7], [8]], [5, 6, 7, 8])

        # print X_train.shape
        # print y_train.shape
        # print X_test.shape
        # print y_test.shape

        # print X_train
        # print y_train
        # print X_test
        # print y_test

        # Make the logistic model
        # logistic = linear_model.LogisticRegression()
        # logistic_regres = logistic.fit(X_train, y_train)
        # print('Logistic score: %f' % logistic_regres.score(X_test, y_test))
        #.Lasso(alpha=0.1)

        # for i in range(X_test):
        # print (len(X_test))

        # Make the linear model
        linear = linear_model.Lasso(alpha=.1)
        linear_regres = linear.fit(X_train, y_train)
        print('Linear predicted value: ' + str(linear_regres.predict(X_test)))

        print test_set[0]['source']

        # print

        # for w in range(linear_regres.coef_.shape[0]):
        #     if linear_regres.coef_[w] != 0:
        #         print str(linear_regres.coef_[w]) + "\t" + all_words[w]
        #
        # # Predict against the test set
        # print y_test
        # # print logistic_regres.predict(X_test)
        # print linear_regres.predict(X_train[:5])

        # sys.exit()
