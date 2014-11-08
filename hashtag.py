#! /usr/bin/env python

import os
import re
import time
import datetime
import ConfigParser
import tweepy
import bloctweet
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

while True:
	try:
		config = bloctweet.settings()
		bloctweet.get_hash_tweets()
		bloctweet.infomsg('[hashtag]: Waiting for ' + config.refresh + ' seconds...')
		time.sleep(float(config.refresh))
		
	except KeyboardInterrupt:
		bloctweet.cmd_stop()
		break