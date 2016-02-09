import twitter
import config

import json

api = twitter.Api(
	consumer_key=config.CONSUMER_KEY,
	consumer_secret=config.CONSUMER_SECRET,
	access_token_key=config.ACCESS_TOKEN_KEY,
	access_token_secret=config.ACCESS_TOKEN_SECRET)

# print(api.VerifyCredentials())

# Fetch the sequence of public Status messages for a single user
# tweets = api.GetUserTimeline(user_id='cnn', screen_name=None, since_id=None, max_id=None, count=20, 
# 	include_rts=True, trim_user=None, exclude_replies=None)

tweets = api.GetSearch(term='cnn', geocode=None, since_id=None, max_id=None, 
	until=None, count=15, lang=None, locale=None, result_type='mixed', 
	include_entities=None)

for element in tweets:
	print element
	# print json.dumps(element, sort_keys=True, indent=4, separators=(',', ': '))

# api = twitter.Api(consumer_key='consumer_key',
# consumer_secret='consumer_secret',
# access_token_key='access_token',
# access_token_secret='access_token_secret')

