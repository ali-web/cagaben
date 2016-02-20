import twitter
import config
import json
import sys

api = twitter.Api(
	consumer_key=config.CONSUMER_KEY,
	consumer_secret=config.CONSUMER_SECRET,
	access_token_key=config.ACCESS_TOKEN_KEY,
	access_token_secret=config.ACCESS_TOKEN_SECRET)

# print(api.VerifyCredentials())

# Fetch the sequence of public Status messages for a single user
# tweets = api.GetUserTimeline(user_id='cnn', screen_name=None, since_id=None, max_id=None, count=20, 
# 	include_rts=True, trim_user=None, exclude_replies=None)
term 				= 'gun control from:cnn'
geocode				= None
since_id			= None
max_id				= 699605529048571906
until				= None
count				= 100
lang				= None
locale				= None
result_type			= 'popular'
include_entities	= None

tweets = api.GetSearch(term, geocode, since_id, max_id, until, count, lang, locale, result_type, include_entities)

print len(tweets)
for element in tweets:
	element = json.loads(str(element));
	# print json.dumps(element, sort_keys=True, indent=4, separators=(',', ': '))
	# print element
	print element['id']

# api = twitter.Api(consumer_key='consumer_key',
# consumer_secret='consumer_secret',
# access_token_key='access_token',
# access_token_secret='access_token_secret')

