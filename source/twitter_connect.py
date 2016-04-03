import twitter
import json
import pprint
import sys
import crawler as c

api = twitter.Api(
	consumer_key = 'rDfnFU3WZhr3lP3HbMye2V0WB',
	consumer_secret = '04XhoIx8rVvd3gLacVFkjfAiUv11BZaqxNzXgnSyAcdJPq6QwF',
	access_token_key = '4094459654-8dOT9XixHLKPAZkSK0utFD3MlBIPJsi5aO274eF',
	access_token_secret = 'Gnq9z4VWJdNHM6XNHFWkgZY6K23g1jzCQu0OZBpZGqSoa'
)

# print(api.VerifyCredentials())

# Fetch the sequence of public Status messages for a single user
# tweets = api.GetUserTimeline(user_id='cnn', screen_name=None, since_id=None, max_id=None, count=20,
# 	include_rts=True, trim_user=None, exclude_replies=None)
#
# print tweets
# exit()
term 				= 'from:FoxNews gun'
geocode				= None
since_id			= None
max_id				= None
until				= None
count				= 100
lang				= None
locale				= None
result_type			= 'recent'
include_entities	= None

tweets = api.GetSearch(term, geocode, since_id, max_id, until, count, lang, locale, result_type, include_entities)

print len(tweets)
for element in tweets:
	# print type(element)
	element = json.loads(str(element))
	print json.dumps(element, sort_keys=True, indent=4, separators=(',', ': '))

	# print element
	# print element['text']

# api = twitter.Api(consumer_key='consumer_key',
# consumer_secret='consumer_secret',
# access_token_key='access_token',
# access_token_secret='access_token_secret')

