## Your name: Minjee Kim
## The option you've chosen: Option 2

import unittest
import itertools
import collections
import tweepy
import twitter_info # same deal as always...
import json
import sqlite3
import sys
import codecs
from pprint import pprint
from collections import Counter
from collections import defaultdict

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)

##### TWEEPY SETUP CODE:
# Authentication information should be in a twitter_info file...
consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Set up library to grab stuff from twitter with your authentication, and return it in a JSON format 
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

##### END TWEEPY SETUP CODE

## To get and cache data from Twitter:


CACHE_FNAME = "206finalproject_caching.json"
try:
	cache_file = open(CACHE_FNAME,'r')
	cache_contents = cache_file.read()
	cache_file.close()
	CACHE_DICTION = json.loads(cache_contents)
except:
	CACHE_DICTION = {}


# A function to get and cache data based on a search term
def get_search_term(term):   
	unique_identifier = term

	if unique_identifier in CACHE_DICTION:
		print('using cached data for', term)
		twitter_results = CACHE_DICTION[unique_identifier] 

	else:
		print('getting data from internet for', term)
		twitter_results = api.search(term) 
		
		CACHE_DICTION[unique_identifier] = twitter_results 
		
		cache_file = open(CACHE_FNAME,'w')
		cache_file.write(json.dumps(CACHE_DICTION))
		cache_file.close()

	tweet_search_texts = []
	for tweet in twitter_results["statuses"]:
		#print(tweet)
		tweet_textstweet_search_texts.append(tweet)

	return tweet_search_texts

#print(get_search_term("iu"))

# A function to get and cache data about a Twitter user
def get_user_tweets(term):    
	unique_identifier = "twitter_{}".format(term)

	if unique_identifier in CACHE_DICTION:
		print('using cached data for', term)
		twitter_results = CACHE_DICTION[unique_identifier] 

	else:
		print('getting data from internet for', term)
		twitter_results = api.user_timeline(term) 
		
		CACHE_DICTION[unique_identifier] = twitter_results 
		
		cache_file = open(CACHE_FNAME,'w')
		cache_file.write(json.dumps(CACHE_DICTION))
		cache_file.close()

	tweet_user_texts = []
	for tweet in twitter_results:
		tweet_user_texts.append(tweet)

	return tweet_user_texts

## Write function(s) to get and cache data from the OMDB API with a movie title search (Test it out!) http://www.omdbapi.com 


## Define a class Movie.
# The constructor should accept a dictionary that represents a movie.
# - Its title
# - Its director
# - Its IMDB rating
# - A list of its actors (check out the data and consider how to get a list of strings that represent actor names!)
# - The number of languages in the movie
# - __str__ method


## Creat a database file: finalproject.db
# The database file should have 3 tables, and each should have the following columns... 

# table Tweets, with columns:
# - tweet_id (containing the string id belonging to the Tweet itself, from the data you got from Twitter -- note the id_str attribute) -- this column should be the PRIMARY KEY of this table
# - tweet_text (containing the text of the Tweet)
# - user_id (an ID string, referencing the Users table, see below)
# - movie_id (an ID string, referencing the Movie table, see below)
# - num_favs (containing the number of tweets that user has favorited)
# - retweets (containing the integer representing the number of times the tweet has been retweeted)

# table Users, with columns:
# - user_id (containing the string id belonging to the user, from twitter data -- note the id_str attribute) -- this column should be the PRIMARY KEY of this table
# - screen_name (containing the screen name of the user on Twitter)
# - num_favs (containing the number of tweets that user has favorited)
# - description (text containing the description of that user on Twitter, e.g. "Lecturer IV at UMSI focusing on programming" or "I tweet about a lot of things" or "Software engineer, librarian, lover of dogs..." -- whatever it is. OK if an empty string)

# table Movies, with columns:
# - movie_id (primary key)
# - movie_title
# - director
# - num_lang
# - rating
# - top_actor (The top billed (first in the list) actor in the movie)


## Making queries
# Make a query to select all of the records in the Users database. Save the list of tuples in a variable called users_info.

# Make a query that accesses the numbers of times a movie title was mention in tweets, and the number of times those tweets have been favorited -- so I'll be joining the Movie table and the Tweets table.

# Make a query to select all of the tweets (full rows of tweet information) that have been retweeted more than 25 times.


## Use a set comprehension to look for unique names and proper nouns in this big set of text


## Use a Counter in the collections library to find the most common adjective used among the tweets about a movie.



### IMPORTANT: MAKE SURE TO CLOSE YOUR DATABASE CONNECTION AT THE END OF THE FILE HERE SO YOU DO NOT LOCK YOUR DATABASE (it's fixable, but it's a pain). ###


###### TESTS APPEAR BELOW THIS LINE ######
###### Note that the tests are necessary to pass, but not sufficient -- must make sure you've followed the instructions accurately! ######
print("\n\nBELOW THIS LINE IS OUTPUT FROM TESTS:\n")

class Caching(unittest.TestCase):
	def test_cache_diction(self):
		self.assertEqual(type(CACHE_DICTION),type({}),"Testing whether you have a CACHE_DICTION dictionary")
	def test_get_movie_tweets(self):
		res = get_movie_tweets("Logan")
		self.assertEqual(type(res),type(["hi",3]))
	def test_movie_tweets(self):
		self.assertEqual(type(movie_tweets),type([]))

class MoiveTest(unittest.TestCase):
	def test___str__(self):
		#d = Movie({dictionary representing a movie})
		self.assertFalse(type(d.__str__()) != type(""))

class TableTest(unittest.TestCase):
	def test_tweets_1(self):
		conn = sqlite3.connect('finalproject.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==6,"Testing that there are 5 columns in the Tweets table")
		conn.close()
	def test_users_1(self):
		conn = sqlite3.connect('finalproject.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result[0])==4,"Testing that there are 4 columns in the Users database")
		conn.close()

class QueryTest(unittest.TestCase):
	def test_users_info(self):
		self.assertEqual(type(users_info),type([]),"testing that users_info contains a list")
	def test_users_info2(self):
		self.assertEqual(type(users_info[1]),type(("hi","bye")),"Testing that an element in the users_info list is a tuple")

class Task4(unittest.TestCase):
	def test_common_adj(self):
		self.assertEqual(type(most_common_adj),type(""),"Testing that most_common_adj is a string")

if __name__ == "__main__":
	unittest.main(verbosity=2)
