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
		bloctweet.get_dm_tweets()	
		bloctweet.infomsg('[dm]: Waiting for ' + config.dmrefresh + ' seconds...')
		time.sleep(float(config.dmrefresh))
		
	except KeyboardInterrupt:
		bloctweet.cmd_stop()
		break