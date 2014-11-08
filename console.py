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
		cmdinput = raw_input('Enter a command: ')
		if cmdinput == '':
			bloctweet.errmsg('No command entered, use help for a list of commands')
		else:
			args = re.split('\W+', cmdinput)
			if args[0] == 'start':
				bloctweet.cmd_start()
			elif args[0] == 'stop':
				bloctweet.cmd_stop()
			elif args[0] == 'help':
				if len(args) > 1:
					bloctweet.cmd_help(args[1])
				else:
					bloctweet.cmd_help()
			elif args[0] == 'dmpost':
				if len(args) > 1:
					bloctweet.cmd_dmpost(args[1])
				else:
					bloctweet.inval_syn(args[0])
			elif args[0] == 'hashpost':
				if len(args) > 1:
					bloctweet.cmd_hashpost(args[1])
				else:
					bloctweet.inval_syn(args[0])
			elif args[0] == 'signpost':
				if len(args) > 1:
					bloctweet.cmd_signpost(args[1])
				else:
					bloctweet.inval_syn(args[0])
			elif args[0] == 'sethash':
				if len(args) > 1:
					bloctweet.cmd_sethash(args[1])
				else:
					bloctweet.inval_syn(args[0])

			elif args[0] == 'sethashrefresh':
				if len(args) > 1:
					bloctweet.cmd_sethashrefresh(args[1])
				else:
					bloctweet.inval_syn(args[0])	
				
			elif args[0] == 'setdmrefresh':
				if len(args) > 1:
					bloctweet.cmd_setdmrefresh(args[1])
				else:
					bloctweet.inval_syn(args[0])	
					
			elif args[0] == 'adduser':
				if len(args) > 1:
					bloctweet.cmd_adduser(args[1])
				else:
					bloctweet.inval_syn(args[0])	
					
			elif args[0] == 'deluser':
				if len(args) > 1:
					bloctweet.cmd_deluser(args[1])
				else:
					bloctweet.inval_syn(args[0])	
					
			elif args[0] == 'test':
				bloctweet.init_setup()
				#bloctweet.logger()
				# bloctweet.add_user_local(args[1])
				# bloctweet.add_user_twitter(args[1])
			else:
				bloctweet.errmsg('Not a valid command, use help for a list of commands')
			
		time.sleep(1)
		
	except KeyboardInterrupt:
		bloctweet.cmd_stop()
		break