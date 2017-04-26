## Your name: Minjee Kim
## The option you've chosen: Option 2

import unittest
import itertools
import collections
import tweepy
import twitter_info # same deal as always...
import json
import requests
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
def get_twitter_search(term):   
	unique_identifier = "tweet_{}".format(term)

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
		tweet_search_texts.append(tweet)

	return tweet_search_texts


## Write function(s) to get and cache data from the OMDB API with a movie title search (Test it out!) http://www.omdbapi.com 
def get_OMDB_data(term):
	unique_identifier = "movie_{}".format(term)
	base_url = "http://www.omdbapi.com/?t=" + term

	if unique_identifier in CACHE_DICTION:
		print('using cached data')
		return CACHE_DICTION[unique_identifier]
	else:
		print('getting data from internet')
		response = requests.get(base_url)

		CACHE_DICTION[unique_identifier] = response.json()

		cache_file = open(CACHE_FNAME,'w')
		cache_file.write(json.dumps(CACHE_DICTION))
		cache_file.close()

	return CACHE_DICTION[unique_identifier]


## Define a class Movie.
# The constructor should accept a dictionary that represents a movie.
# - Its title
# - Its director
# - Its IMDB rating
# - A list of its actors (check out the data and consider how to get a list of strings that represent actor names!)
# - The number of languages in the movie
# - __str__ method


class Movie():
	def __init__(self, dic={}):
		self.movie_id = dic["imdbID"]
		self.movie_title = dic["Title"]
		self.director = dic["Director"]
		self.rating = dic["imdbRating"]
		self.num_lang = len((dic["Language"].split()))
		self.actors = (dic["Actors"]).split(", ")

	def top_actor(self):
		return self.actors[0]

	def __str__(self):
		return "Movie: {} \nDirector: {} \nRating: {} \nCasts: {}\nLanguages: {}\n".format(self.movie_title,self.director,self.rating,self.actors,self.num_lang)

class Tweet():
	def __init__(self, dic={}):
		self.tweet_id = dic['id_str']
		self.tweet_text = dic['text']
		self.user_id = dic['user']['id_str']
		self.num_favs = dic['user']['favourites_count']
		self.retweets = dic['retweet_count']
		self.screen_name = dic['user']['screen_name']
		self.description = dic['user']['description']
		if len(dic['entities']['user_mentions']) != 0:
			for a in dic['entities']['user_mentions']:
				self.user_id = a['id_str']
				self.screen_name = a['screen_name']
				user_results = api.get_user(a['id'])
				self.num_favs = user_results['favourites_count']
				self.description = user_results['description']


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


conn = sqlite3.connect('finalproject.db')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Tweets')

table_spec = 'CREATE TABLE IF NOT EXISTS '
table_spec += 'Tweets (tweet_id TEXT PRIMARY KEY, '
table_spec += 'tweet_text TEXT, user_id TEXT, screen_name TEXT, num_favs INTEGER, retweets INTEGER, search_term TEXT)'
cur.execute(table_spec)

cur.execute('DROP TABLE IF EXISTS Users')

table_spec = 'CREATE TABLE IF NOT EXISTS '
table_spec += 'Users (user_id TEXT PRIMARY KEY, '
table_spec += 'screen_name TEXT, num_favs INTEGER, description TEXT)'
cur.execute(table_spec)

cur.execute('DROP TABLE IF EXISTS Movies')

table_spec = 'CREATE TABLE IF NOT EXISTS '
table_spec += 'Movies (movie_id TEXT PRIMARY KEY, '
table_spec += 'movie_title TEXT, director TEXT, num_lang INTEGER, rating INTEGER, top_actor TEXT)'
cur.execute(table_spec)


movies = ["logan", "guardians of the galaxy", "zootopia", "the shawshank redemption"]

movie_data = []
movie_tweets = []
movie_id_list = []

for each_movie in movies:
	movie_data.append(get_OMDB_data(each_movie))

for each in movie_data: # Movie table
	m = Movie(each)
	movie_id = m.movie_id
	movie_id_list.append(movie_id)
	movie_title = m.movie_title
	director = m.director
	rating = m.rating
	num_lang = m.num_lang
	top_actor = m.top_actor()
	#print(m.__str__())

	cur.execute('INSERT INTO Movies (movie_id, movie_title, director, num_lang, rating, top_actor) VALUES (?, ?, ?, ?, ?, ?)', (movie_id, movie_title, director, num_lang, rating, top_actor))

for each_movie in movies: # Tweet and User table
	movie_tweets = get_twitter_search(each_movie)
	search_term = each_movie
	for each_tweet in movie_tweets:
		t = Tweet(each_tweet)
		tweet_id = t.tweet_id
		tweet_text = t.tweet_text
		user_id = t.user_id
		num_favs = t.num_favs
		retweets = t.retweets
		screen_name = t.screen_name
		description = t.description

		cur.execute('INSERT INTO Tweets (tweet_id, tweet_text, user_id, screen_name, num_favs, retweets, search_term) VALUES (?, ?, ?, ?, ?, ?, ?)', (tweet_id, tweet_text, user_id, screen_name, num_favs, retweets, search_term))
		cur.execute('INSERT OR IGNORE INTO Users (user_id, screen_name, num_favs, description) VALUES (?, ?, ?, ?)', (user_id, screen_name, num_favs, description))


conn.commit()


## Making queries

# Make a query to select all of the records in the Users database. Save the list of tuples in a variable called users_info.
query = 'SELECT * FROM Users'
cur.execute(query)
users_info = []
for row in cur:
	users_info.append(row)

# Make a query to select all of the user screen names from the database. Save a resulting list of strings (NOT tuples, the strings inside them!) in the variable screen_names. HINT: a list comprehension will make this easier to complete!

query = 'SELECT movie_title FROM Movies WHERE rating >= 8.5'
cur.execute(query)
best_movies = []
for row in cur:
	best_movies.append(row[0])

#print(best_movies)


# Make a query that accesses the numbers of times a movie title was mention in tweets, and the number of times those tweets have been favorited -- so I'll be joining the Movie table and the Tweets table.

# Make a query using an INNER JOIN to get a list of tuples with 2 elements in each tuple: the user screenname and the text of the tweet -- for each tweet that has been retweeted more than 50 times. Save the resulting list of tuples in a variable called joined_result.

cur.execute("SELECT Tweets.search_term FROM Users INNER JOIN Tweets ON Users.user_id = Tweets.user_id WHERE Users.num_favs > 10000")
query = cur.fetchall()
for a in query:
	print(a[0])


#joined_result = []
#for row in cur:
#	joined_result.append((row[1],row[0]))

#print(joined_result)

# Make a query to select all of the tweets (full rows of tweet information) that have been retweeted more than 100 times.

query = 'SELECT * FROM Tweets'
cur.execute(query)
more_than_100_rts = []
for row in cur:
	if row[-2] > 100:
		more_than_100_rts.append(row[1])

#print(more_than_100_rts)


## Use a set comprehension to look for unique names and proper nouns in this big set of text


## Use a Counter in the collections library to find the most common adjective used among the tweets about a movie.



### IMPORTANT: MAKE SURE TO CLOSE YOUR DATABASE CONNECTION AT THE END OF THE FILE HERE SO YOU DO NOT LOCK YOUR DATABASE (it's fixable, but it's a pain). ###

conn.close()

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
