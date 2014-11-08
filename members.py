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
		api = bloctweet.getauth()
		bloctweet.infomsg('[members]: Syncing contributor list with twitter...')
		internet = bloctweet.checktwitterlist()
		local = bloctweet.checklocallist()
		
		addlist = bloctweet.comparelists(local, internet) #adds users
		for each_add in range(len(addlist)):
			bloctweet.add_user_twitter(addlist[each_add])
			api.create_friendship(screen_name=addlist[each_add])
			
		dellist = bloctweet.comparelists(internet, local) #removes users
		for each_del in range(len(dellist)):
			bloctweet.del_user_twitter(dellist[each_del])
		bloctweet.infomsg('[members]: Sync complete')
	
		time.sleep(300)
		
	except KeyboardInterrupt:
		bloctweet.cmd_stop()
		break