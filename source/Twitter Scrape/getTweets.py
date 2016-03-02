import got

import sys
import time
from datetime import datetime

from pprint import pprint


import dateutil.relativedelta  # For converting months

from pymongo import MongoClient


def jsonifyTweetObj(tweetObj):
	jsonObj = {
		'topic'   : '',
		'source'   : '',
		'link'	  : '',
		'title'	  : '',
		'content' : '',
		'twitter' : {
			'body'		: tweetObj.text,
			'id' 		: tweetObj.id,
			'link' 		: tweetObj.permalink,
			'date'		: tweetObj.date,
			'favs' 		: tweetObj.favorites,
			'retweets' 	: tweetObj.retweets,
			'hashtags' 	: tweetObj.hashtags,
			'mentions' 	: tweetObj.mentions
		}
	}
	return jsonObj

def subtractMonth(dateStr):
	# Convert string to date object
	dateObj = datetime.strptime(dateStr, '%Y-%m-%d')
	# Subtract a month from the dateObj
	earlierObj = dateObj - dateutil.relativedelta.relativedelta(months=1)
	# Convert the object back into a date string
	earlierStr = earlierObj.strftime("%Y-%m-%d")
	return earlierStr

def main():
	cl = MongoClient()
	coll = cl.cagaben.story

	docs = [{"_id" : 1, "foo" : "HELLO"}, {"_id" : 2, "Blah" : "Bloh"}]

	# for doc in docs:
	# 	coll.save(doc)

	def printTweet(descr, t):
		print descr
		print "Username: %s" % t.username
		print "Date: %s" % t.date
		# print "Retweets: %d" % t.retweets
		print "Text: %s" % t.text
		# print "Mentions: %s" % t.mentions
		# print "Hashtags: %s\n" % t.hashtags
		print "Link: %s\n" % t.permalink


	# The current date for the algorithm
	today = datetime.now().strftime("%Y-%m-%d")

	## Variables that Define the Database ##
	numTweets = 10

	topics = [
		'gun control'
	]

	newsSources = [
		'cnn',
		'FoxNews',
		'washtimes',
		'wsj',
		'usnews',
		'latimes',
		'usatoday',
		'gma'
	]

	finalTweets = {}

	# For each topic
	for t in xrange(len(topics)):
		finalTweets[topics[t]] = {}  # Add an object for that topic

		# For each news source
		for i in xrange(len(newsSources)):
			finalTweets[topics[t]][newsSources[i]] = []  # Add a list for all the tweets

			# initialize the range to be from today to a month ago
			dateRange = { 's':subtractMonth(today), 'u':today }

			while(len(finalTweets[topics[t]][newsSources[i]]) < numTweets):
				print dateRange

				# Set the tweet criteria
				tweetCriteria = got.manager.TweetCriteria()\
					.setUsername(newsSources[i]) \
					.setQuerySearch(topics[t]) \
					.setSince(dateRange['s']) \
					.setUntil(dateRange['u']) \
					.setMaxTweets(5)

				# Retrieve the tweets
				print "Retrieving Tweets . . ."
				tweets = got.manager.TweetManager.getTweets(tweetCriteria)
				if (len(tweets) != 0):

					# Loop through the results, looking for tweets that match our criteria
					for j in reversed(xrange(len(tweets))):
						print j
						text = tweets[j].text
						
						print '\nTweet: '
						printTweet("New Tweet:", tweets[j])

						httpStart = text.find('http')
						if httpStart != -1:
							httpEnd = text.find(' ', httpStart)
							link = text[httpStart : httpEnd]
							print 'Link in Tweet: '
							print link

							jsonTweet = jsonifyTweetObj(tweets[j])
							jsonTweet['topic'] = topics[t]
							jsonTweet['link'] = link
							jsonTweet['source'] = newsSources[i]

							finalTweets[topics[t]][newsSources[i]].append(jsonTweet)
					
						if (len(finalTweets[topics[t]][newsSources[i]]) >= numTweets):
							print 'There are: ' + str(len(finalTweets[topics[t]][newsSources[i]])) + ' Tweets with links'
							break

				# Update the date range for the next iteration
				dateRange['u'] = dateRange['s']
				dateRange['s'] = subtractMonth(dateRange['u'])

	print '\n\n\n\n\n\n\n\n\n\n'
	pprint(finalTweets)

	stories = []

	for topic in topics:
		for source in newsSources:
			for story in xrange(len(finalTweets[topic][source])):
				stories.append(finalTweets[topic][source][story])

	for story in stories:
		coll.save(story)




if __name__ == '__main__':
	main()