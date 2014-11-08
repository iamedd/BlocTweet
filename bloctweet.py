#! /usr/bin/env python

import time
import os
import datetime
import logging
import ConfigParser
import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

def curtime():
	data = "[" + str(datetime.datetime.now()) + ']'
	return data
	
def infomsg(msg, log='no'):
	print(curtime() + '[INFO]' + msg)
	if log == 'yes':
		logger('main', 'info', msg)

def errmsg(msg, log='no'):
	print(curtime() + '[ERROR]' + msg)
	if log == 'yes':
		logger('main', 'error', msg)

def warnmsg(msg, log='no'):
	print(curtime() + '[WARNING!]' + msg)
	if log == 'yes':
		logger('main', 'warning', msg)
		
		

def logger(logfile, type, msg):
	config = settings()
	if config.count == '0':
		logging.getLogger('').setLevel(logging.DEBUG)
		filehandle = logging.FileHandler('logs/' + logfile + '.log')
		filehandle.setLevel(logging.INFO)
		formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s')
		filehandle.setFormatter(formatter)
		logging.getLogger('').addHandler(filehandle)
		write_conf('settings', 'count', '1')
		
	data = logging.getLogger('colog.' + logfile)
	if type == 'debug':
		data.debug(msg)
	elif type == 'info':
		data.info(msg)
	elif type == 'warning':
		data.warning(msg)
	elif type == 'error':
		data.error(msg)
		
class settings:
	def __init__(self):
		config = ConfigParser.ConfigParser()
		config.read('settings.ini')
		self.account = config.get('settings','account_name')
		self.refresh = config.get('settings','refresh_rate')
		self.co_tag = config.get('settings','search_hash')
		self.hash_on = config.get('settings','hashtag_enabled')
		self.dm_on = config.get('settings','dm_enabled')
		self.sign_on = config.get('settings','signing_enabled')
		self.c_key = config.get('keys','consumer_key')
		self.c_secret = config.get('keys','consumer_secret')
		self.a_token = config.get('keys','access_token')
		self.a_secret = config.get('keys','access_token_secret')
		self.list = config.get('settings','list_id')
		self.dmrefresh = config.get('settings', 'dm_refresh_rate')
		self.count = config.get('settings', 'count')

class command:
	def __init__(self, cmdv, syntax, desc, defaultv=None, curr=None, warnv=None):
		self.cmd = cmdv
		self.syn = syntax
		self.des = desc
		self.default = defaultv
		self.cur = curr
		self.warn = warnv

def get_cmdinfo(value):
	config = settings()	
	adduser = command('adduser','adduser <username>', 'Adds a contributor to the account')
	deluser = command('deluser', 'deluser <username>', 'Removes a contributor to the account')
	dmpost = command('dmpost', 'dmpost <0 = off | 1 = on>', 'Allows contributors to post to the account via DM', '1', config.dm_on)
	hashpost = command('hashpost', 'hashpost <0 = off | 1 = on>', 'Allows contributors to post to the account via hashtag', '1', config.hash_on)
	help = command('help', 'help (cmd)', 'Lists availible commands')
	setdmrefresh = command('setdmrefresh', 'setdmrefresh <seconds>', 'Sets the interval in seconds to search for new posts via DM', '90', config.dmrefresh, 'Values of 60 seconds or below will cause you to hit the rate limit')
	sethash = command('sethash', 'sethash <hashtag>', 'Defines the hashtag to be used in posting to the account', 'CT', config.co_tag)
	sethashrefresh = command('sethashrefresh', 'sethashrefresh <seconds>', 'Sets the interval in seconds to search for new posts via hashtag', '30', config.refresh, 'Values of 5 seconds or below will cause you to hit the rate limit')
	signpost = command('signpost', 'signpost <0 = off | 1 = on>', 'Posts by contributors are signed (via @username)', '0', config.sign_on)
	start = command('start', 'start', 'Starts BlocTweet')
	stop = command('stop', 'stop', 'Stops BlocTweet')
	version = command('version', 'version', 'Displays the version of BlocTweet running')
	for data in (adduser, deluser, dmpost, hashpost, help, setdmrefresh, sethash, sethashrefresh, signpost, start, stop, version):
		if data.cmd == value:
			return data

	
def getauth():
	config = settings()
	auth = tweepy.OAuthHandler(config.c_key, config.c_secret)
	auth.set_access_token(config.a_token, config.a_secret)
	api = tweepy.API(auth)
	return api
	
def write_conf(type, setting, value):
	data = ConfigParser.ConfigParser()
	data.read('settings.ini')
	data.set(type, setting, value)
	fileh = open('settings.ini', 'wb')
	try:
		data.write(fileh)
	finally:
		fileh.close()
		infomsg('Updated values for ' + setting + ' to ' + value, 'yes')
		
def write_cache(type, setting, value):
	data = ConfigParser.ConfigParser()
	data.read('cache.ini')
	data.set(type, setting, value)
	fileh = open('cache.ini', 'wb')
	try:
		data.write(fileh)
	finally:
		fileh.close()
		infomsg('Updated cache values for ' + type + ' / ' + setting + ' to ' + value, 'yes')
		
def get_listid(lists):
	infomsg('Retrieving list ID...')
	for each_list in range(len(lists)):
		if lists[each_list].slug == 'bloctweet':
			infomsg('List ID found - ' + lists[each_list].id_str)
			write_conf('settings', 'list_id', lists[each_list].id_str)
			return lists[each_list].id_str
		
def make_list():
	api = getauth()
	infomsg('Creating contributor list...', 'yes')
	api.create_list(name='BlocTweet', mode='private')
	infomsg('Contributor list creation succesful', 'yes')

def cmd_sethash(data):
	config = settings()
	value = data.strip('#').lower()
	if value != config.co_tag:
		write_conf('settings', 'search_hash', value)
	else:
		errmsg('hashtag is already set to ' + value)

	
def help_list(obj):
	print('     ' + obj.syn + ' - ' + obj.des)

	
def gen_help(syn, desc, default, curr, warn):
	print('##################################################')
	print('     ' + desc)
	print('          SYNTAX : "' + syn + '"')
	if default is not None:
		print('          DEFAULT : ' + default)
	if curr is not None:
		print('          CURRENT : ' + curr)
	if warn is not None:
		print('          WARNING : ' + warn)
	print('##################################################')

def inval_syn(cmd):
	errmsg('INVALID SYNTAX ERROR')
	infomsg('SYNTAX: ' + get_cmdinfo(cmd).syn + ' - ' + get_cmdinfo(cmd).des)


def cmd_help(value=None):
	config = settings()
	if value is None:
		help_list(get_cmdinfo('adduser'))
		help_list(get_cmdinfo('deluser'))
		help_list(get_cmdinfo('dmpost'))
		help_list(get_cmdinfo('hashpost'))
		help_list(get_cmdinfo('help'))
		help_list(get_cmdinfo('setdmrefresh'))
		help_list(get_cmdinfo('sethash'))
		help_list(get_cmdinfo('sethashrefresh'))
		help_list(get_cmdinfo('signpost'))
		help_list(get_cmdinfo('start'))
		help_list(get_cmdinfo('stop'))
		help_list(get_cmdinfo('version'))
	else:
		cmd_obj = get_cmdinfo(value)
		gen_help(cmd_obj.syn, cmd_obj.des, cmd_obj.default, cmd_obj.cur, cmd_obj.warn)

def cmd_dmpost(value):
	config = settings()
	if (value == "0") or (value == "1"):
		if value != config.dm_on:
			write_conf('settings', 'dm_enabled', value)
		else:
			errmsg('dmpost is already set to ' + value)
	else:
		inval_syn('dmpost')
		
def cmd_hashpost(value):
	config = settings()
	if (value == "0") or (value == "1"):
		if value != config.hash_on:
			write_conf('settings', 'hashtag_enabled', value)
		else:
			errmsg('hashpost is already set to ' + value)
	else:
		inval_syn('hashpost')
		
def cmd_signpost(value):
	config = settings()
	if (value == "0") or (value == "1"):
		if value != config.sign_on:
			write_conf('settings', 'signing_enabled', value)
		else:
			errmsg('signpost is already set to ' + value)
	else:
		inval_syn('signpost')
		
def cmd_sethashrefresh(value):
	config = settings()
	if value.isdigit() is True:
		if int(value) > 5:
			if value != config.refresh:
				write_conf('settings', 'refresh_rate', value)
			else:
				errmsg('hashrefresh is already set to ' + value)
		else:
			warnmsg(get_cmdinfo('sethashrefresh').warn)
	else:
		inval_syn('sethashrefresh')
		
def cmd_setdmrefresh(value):
	config = settings()
	if value.isdigit() is True:
		if int(value) > 60:
			if value != config.dmrefresh:
				write_conf('settings', 'dm_refresh_rate', value)
			else:
				errmsg('dmrefresh is already set to ' + value)
		else:
			warnmsg(get_cmdinfo('setdmrefresh').warn)
	else:
		inval_syn('setdmrefresh')
	
def cmd_start():
	config = settings()
	write_conf('settings', 'count', '0')
	infomsg('Starting BlocTweet...', 'yes')

	infomsg('[members]: Loading membership module...', 'yes')
	os.system('python members.py &')
	infomsg('[members]: Membership module loaded', 'yes')
	if config.hash_on == '1':
		infomsg('[hashtag]: Loading hashtag module...', 'yes')
		os.system('python hashtag.py &')
		infomsg('[hashtag]: Hashtag module loaded', 'yes')
	else:
		infomsg('[hashtag]: Skipping loading hashtag module...', 'yes')
	if config.dm_on == '1':
		infomsg('[dm]: Loading DM module...', 'yes')
		os.system('python dm.py &')
		infomsg('[dm]: DM module loaded', 'yes')
	else:
		infomsg('[dm]: Skipping loading DM module...', 'yes')
		
def cmd_stop():
	infomsg('Exiting BlocTweet...', 'yes')
	os.system('pkill python')
	
def get_hash_tweets():		
	config = settings()
	api = getauth()
	cache_tweet = []
	cache_id = []
	cache_user = []
	cache = ConfigParser.ConfigParser()
	cache.read('cache.ini')
	if cache.get('main', 'hash') == '0':
		tquery = api.list_timeline(list_id=config.list, include_rts='0', count='50')
	else:
		tquery = api.list_timeline(list_id=config.list, include_rts='0', count='50', since_id=cache.get('main', 'hash'))
	infomsg('[hashtag]: Searching for tweets via hashtag...')
	for each_tweet in range(len(tquery)):
		ents = tquery[each_tweet].entities
		tagscont = ents['hashtags']
		for each_cont in range(len(tagscont)):
			finalcont = tagscont[each_cont]
			if finalcont['text'] == config.co_tag:
				tweettext = tquery[each_tweet].text
				tweetid = tquery[each_tweet].id_str
				tweetsender = tquery[each_tweet].user.screen_name.lower()
				infomsg('[hashtag]: Found a tweet from @' + tweetsender + ': ' + tweettext, 'yes')
				logger(tweetsender, 'info', '[hashtag]: Found a tweet from @' + tweetsender + ': ' + tweettext)
				cache_tweet.append(tweettext)
				cache_id.append(tweetid)
				cache_user.append(tweetsender)
	infomsg('[hashtag]: Caching search results...')
	try:
		write_cache('main', 'hash', tquery[0].id_str)	
		cache_tweet.reverse()
		cache_id.reverse()
		cache_user.reverse()
		infomsg('[hashtag]: Sending found tweets...')
		for num in range(len(cache_tweet)):
			send_tweets('hashtag', cache_user[num], cache_id[num], cache_tweet[num])
		
	except IndexError:
		infomsg('[hashtag]: No new tweets found')
		pass

def get_dm_tweets():		
	config = settings()
	api = getauth()
	cache_tweet = []
	cache_id = []
	cache_user = []
	DMs = api.direct_messages(count=50)
	listofmems = checklocallist()
	infomsg('[dm]: Searching for tweets via DM...')
	for each_dm in range(len(DMs)):
		for each_mem in range(len(listofmems)):
			if listofmems[each_mem] == DMs[each_dm].sender_screen_name:
				infomsg('[dm]: Found a tweet from @' + DMs[each_dm].sender_screen_name + ': ' + DMs[each_dm].text, 'yes')
				logger(DMs[each_dm].sender_screen_name, 'info', '[dm]: Found a tweet from @' + DMs[each_dm].sender_screen_name + ': ' + DMs[each_dm].text)
				cache_user.append(DMs[each_dm].sender_screen_name)
				cache_id.append(DMs[each_dm].id_str)
				cache_tweet.append(DMs[each_dm].text)
	infomsg('[dm]: Caching search results...')
	try:
		cache_tweet.reverse()
		cache_id.reverse()
		cache_user.reverse()
		infomsg('[dm]: Sending found tweets...')
		for num in range(len(cache_tweet)):
			send_tweets('dm', cache_user[num], cache_id[num], cache_tweet[num])
	except IndexError:
		infomsg('[dm]: No new tweets found')
		pass
		
def send_tweets(method, user, tid, tweet):
	config = settings()
	cache = ConfigParser.ConfigParser()
	cache.read('cache.ini')
	api = getauth()
	if method == 'hashtag':
		if tid > cache.get(user, 'hash'):
			infomsg('[hashtag]: Sending tweet from @' + user + '..')
			api.update_status(tweet)
			infomsg('[' + user + ' via hashtag]: ' + tweet, 'yes')
			logger(user, 'info', '[' + user + ' via hashtag]: ' + tweet)
			infomsg('[hashtag]: Updating @' + user + "'s cache...")
			write_cache(user, 'hash', tid)
	if method == 'dm':
		if tid > cache.get(user, 'dm'):
			infomsg('[dm]: Sending tweet from @' + user + '..')
			api.update_status(tweet)
			infomsg('[' + user + ' via dm]: ' + tweet, 'yes')
			logger(user, 'info', '[' + user + ' via dm]: ' + tweet)
			infomsg('[dm]: Updating @' + user + "'s cache...")
			write_cache(user, 'dm', tid)
			infomsg('[dm]: Deleting sent DM...')
			api.destroy_direct_message(tid)
			infomsg('[dm]: DM deleted')


def checktwitterlist():
	config = settings()
	api = getauth()
	listofmems = []
	listmems = api.list_members(list_id=config.list)
	for each_mem in range(len(listmems)):
		listofmems.append(listmems[each_mem].screen_name.lower())
	return listofmems
	
def checklocallist():
	config = ConfigParser.ConfigParser()
	config.read('settings.ini')
	listofmems = config.options('contributors')
	return listofmems

def comparelists(locallist, twitterlist):
	data = []
	for each_local in range(len(locallist)):
		if str(twitterlist.count(locallist[each_local])) == '0':
			data.append(locallist[each_local])
	return data


def cmd_adduser(user):
	api = getauth()
	data = user.strip('@').lower()
	listofmems = checklocallist()
	if str(listofmems.count(data)) == '0':
		add_user_local(data)
		add_user_twitter(data)
		api.create_friendship(screen_name=data)
	else:
		errmsg('@' + data + ' is already a contributor')
		
def cmd_deluser(user):
	data = user.strip('@').lower()
	listofmems = checklocallist()
	if str(listofmems.count(data)) != '0':
		del_user_local(data)
		del_user_twitter(data)
	else:
		errmsg('@' + data + ' is not a contributor')
	
def add_user_local(user):
	data = ConfigParser.ConfigParser()
	data.read('cache.ini')
	infomsg('Adding @' + user + ' to local memberlist...')
	write_conf('contributors', user, '0')
	try:
		write_cache(user, 'dm', '0')
		write_cache(user, 'hash', '0')
	finally:
		infomsg('Adding of @' + user + ' to local memberlist complete', 'yes')
		logger(user, 'info', 'Adding of @' + user + ' to local memberlist complete')

def del_user_local(user):
	data = ConfigParser.ConfigParser()
	data.read('cache.ini')
	data2 = ConfigParser.ConfigParser()
	data2.read('settings.ini')
	infomsg('Removing @' + user + ' from local memberlist...')
	data2.remove_option('contributors', user)
	data.remove_section(user)
	fileh = open('cache.ini', 'wb')
	fileh2 = open('settings.ini', 'wb')
	try:
		data.write(fileh)
		data2.write(fileh2)
	finally:
		fileh.close()
		fileh2.close()
		infomsg('Removal of @' + user + ' from local memberlist complete', 'yes')
		logger(user, 'info', 'Removal of @' + user + ' from local memberlist complete')

def del_user_twitter(user):
	config = settings()
	api = getauth()	
	infomsg('Removing @' + user + 'from twitter memberlist...')
	api.remove_list_member(list_id=config.list, screen_name=user)
	infomsg('Removing of @' + user + ' from twitter memberlist complete', 'yes')
	logger(user, 'info', 'Removing of @' + user + ' from twitter memberlist complete')

def add_user_twitter(user):
	config = settings()
	api = getauth()
	infomsg('Adding @' + user + ' to twitter memberlist...')
	api.add_list_member(list_id=config.list, screen_name=user)
	infomsg('Adding of @' + user + ' to twitter memberlist complete', 'yes')
	logger(user, 'info', 'Adding of @' + user + ' to twitter memberlist complete')
	
def init_setup():
	api = getauth()
	infomsg('[Setup] Starting BlocTweet setup...')
	while True:
		accountinput = raw_input('Enter account name: ')
		if accountinput == '':
			errmsg('No account name entered')
			pass
		else:
			write_conf('settings', 'account_name', accountinput.strip('@').lower())
			break
	config = settings()
	infomsg('[Setup] Creating BlocTweet list')
	make_list()
	infomsg('[Setup] Getting list id')
	lists = api.lists_all(screen_name=config.account)
	infomsg('[Setup] Saving list id')
	write_conf('settings', 'list_id', get_listid(lists))
	while True:
		dminput = raw_input('Enable tweeting via DM (1=y, 0=n)?: ')
		if dminput == '':
			errmsg('No value entered')
			pass
		elif (dminput == "0") or (dminput == "1"):
			cmd_dmpost(dminput)
			break
		else:
			errmsg('Invalid value entered, must be 0 or 1')
			pass
	while True:
		hashinput = raw_input('Enable tweeting via Hashtag (1=y, 0=n)?: ')
		if hashinput == '':
			errmsg('No value entered')
			pass
		elif (hashinput == "0") or (hashinput == "1"):
			cmd_hashpost(hashinput)
			while True:
				settaginput = raw_input('Set hashtag to use: ')
				if settaginput == '':
					errmsg('No value entered')
					pass
				else:
					cmd_sethash(settaginput)
					break
				
			break
		else:
			errmsg('Invalid value entered, must be 0 or 1')
			pass
	while True:
		userinput = raw_input('Add contributor, enter "done" when finished: ')
		if userinput == '':
			errmsg('No username entered')
			pass
		elif userinput.lower() == 'done':
			break
		else:
			cmd_adduser(userinput)
			pass
	infomsg('[Setup] Setup complete')