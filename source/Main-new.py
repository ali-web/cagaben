import sys
import time
from datetime import datetime
import json

from pprint import pprint


import dateutil.relativedelta  # For converting months

import re
from pymongo import MongoClient

import twitter
import crawler as c




api = twitter.Api(
	consumer_key = 'rDfnFU3WZhr3lP3HbMye2V0WB',
	consumer_secret = '04XhoIx8rVvd3gLacVFkjfAiUv11BZaqxNzXgnSyAcdJPq6QwF',
	access_token_key = '4094459654-8dOT9XixHLKPAZkSK0utFD3MlBIPJsi5aO274eF',
	access_token_secret = 'Gnq9z4VWJdNHM6XNHFWkgZY6K23g1jzCQu0OZBpZGqSoa'
)



def jsonifyTweetObj(tweetObj):
	jsonObj = {
		'topic'   : '',
		'source'   : '',
		'link'	  : '',
		'title'	  : '',
		'content' : '',
		'twitter' : {
			'body'		: tweetObj['text'],
			'id' 		: tweetObj['id'],
			# 'link' 		: tweetObj.permalink,
			'date'		: tweetObj['created_at'],
			'favs' 		: tweetObj.get('favorite_count', None),
			'retweets' 	: tweetObj.get('retweet_count', None),
			# 'hashtags' 	: tweetObj.hashtags,
			# 'mentions' 	: tweetObj.mentions
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
	coll = cl.cagaben6.story

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
	# numTweets = 100

	topics = [
		'all',
		#'gun control',
		#'climate change',
		#'refugee',
		# 'isis',
		# 'obamacare',
	]

	newsSources = [
		'washtimes', #1
		# 'FoxNews', #2
		#### 'NewsHour', #3
		# 'cnn', #4
		###'gma', #5
		# 'usatoday', #6
		####'usnews', #7
		# 'latimes', #8
		# 'CBSNews', #9
		# 'nytimes', #10
		# 'washingtonpost', #11
		#### 'wsj', #11 - not good
	]

	finalTweets = {}

	# For each topic
	for t in xrange(len(topics)):
		finalTweets[topics[t]] = {}  # Add an object for that topic

		# For each news source
		for i in xrange(len(newsSources)):
			finalTweets[topics[t]][newsSources[i]] = []  # Add a list for all the tweets

			term 				= 'from:' + newsSources[i]
			geocode				= None
			since_id			= None
			max_id				= None
			until				= None
			count				= 100
			lang				= None
			locale				= None
			result_type			= 'recent'
			include_entities	= None

			for r in range(1,10):

				print "round " + str(r) + " started"

				# if newsSources[i] in ['gma', 'usnews', 'nytimes']:
				# 	numTweets = 5
				# else:
				# 	numTweets = 10

				# initialize the range to be from today to a month ago
				# dateRange = { 's':subtractMonth(today), 'u':today }

				# while(len(finalTweets[topics[t]][newsSources[i]]) < numTweets):
					# print dateRange

					# Set the tweet criteria
					# tweetCriteria = got.manager.TweetCriteria() \
					# 	.setUsername(newsSources[i]) \
					# 	.setMaxTweets(500)
						#.setSince(dateRange['s']) \
						#.setUntil(dateRange['u']) \
					# .setQuerySearch(topics[t]) \

					# Retrieve the tweets
				print "Retrieving Tweets . . ."



				tweets = api.GetSearch(term, geocode, since_id, max_id, until, count, lang, locale, result_type, include_entities)

				# for element in tweets:
				# 	element = json.loads(str(element))
					# print json.dumps(element, sort_keys=True, indent=4, separators=(',', ': '))


				if len(tweets) != 0:

					# Loop through the results, looking for tweets that match our criteria

					for j, tweet in enumerate(tweets):
						print str(j) + " -"
						tweet = json.loads(str(tweet))

						print str(tweet['id']) + " " + tweet['text']
						print tweet['created_at']
						print "\n"

						# httpStart = text.find('http')
						if 'urls' in tweet:

							link = tweet['urls'].itervalues().next()
							# httpEnd = text.find(' ', httpStart)
							# link = text[httpStart : httpEnd]
							# link = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)[0]

							if link.find('twimg') != -1:
								continue
							print 'Link in Tweet: '
							print link
							print c.pageExists(link)
							if c.pageExists(link) not in [200, 301, 302, 303]:
								print "This link doesn't exist: " + link
								continue
								#sys.exit()

							jsonTweet = jsonifyTweetObj(tweet)
							jsonTweet['topic'] = topics[t]
							jsonTweet['link'] = link
							jsonTweet['source'] = newsSources[i]


							try:
								for tw in finalTweets[topics[t]][newsSources[i]]:
									if tw['title'] == link:
										print "duplicate story"
										raise StopIteration
							except StopIteration:
								continue

							try:
								jsonTweet['title'], jsonTweet['content'] = \
									c.scrapeContent(jsonTweet['link'], jsonTweet['source'])
							except:
								print "the page doesn't exist anymore"
								continue

							if len(jsonTweet['content']) < 100:
								print "news content not available"
								continue
							try:
								for tw2 in finalTweets[topics[t]][newsSources[i]]:
									if tw2['title'] == jsonTweet['title']:
										print "duplicate story"
										raise StopIteration
							except StopIteration:
								continue


							# if link in finalTweets[topics[t]][newsSources[i]]:
							# 	print "duplicate story"
							# 	continue

							finalTweets[topics[t]][newsSources[i]].append(jsonTweet)


						# if j == len(tweets) - 1:
						if tweet.get('id'):
							max_id = tweet['id']
						# print "yesssssss"
						# else:
						# 	print j
						# 	print len(tweets)

					print "max_id updated to: " + str(max_id)
				# exit()

					# if (len(finalTweets[topics[t]][newsSources[i]]) >= numTweets):
					# 	print 'There are: ' + str(len(finalTweets[topics[t]][newsSources[i]])) + ' Tweets with links'
					# 	break

			# print "we got this many tweets:"
			# print len(finalTweets[topics[t]][newsSources[i]])
			# sys.exit()

			# Update the date range for the next iteration
			# dateRange['u'] = dateRange['s']
			# dateRange['s'] = subtractMonth(dateRange['u'])

	print '\n\n\n\n\n\n\n\n\n\n'
	pprint(finalTweets)


	# convert finalStories to an array of all tweets and save to a mongo collection called "story"
	stories = []

	for topic in topics:
		for source in newsSources:
			for story in xrange(len(finalTweets[topic][source])):
				stories.append(finalTweets[topic][source][story])


	#get data from news web page
	# for story in stories:
	# 	print "retrieving story from " + story['source']
	# 	story['title'], story['content'] =\
	# 		c.scrapeContent(story['link'], story['source'])

	# for story in stories:
	# 	print(story)

	# save into mongodb
	print "saving in mongo"
	for story in stories:
		coll.save(story)




if __name__ == '__main__':
	main()