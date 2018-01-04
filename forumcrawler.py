#!python
from __future__ import print_function
import urllib
import re
import itertools
from optparse import OptionParser
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class Player:
	def __init__(self, name, postcount):
		self.name = name
		self.postcount = postcount

class Criteria:
	def __init__(self, postcount, clan_dict):
		self.postcount = postcount
		self.clan_dict = clan_dict

def wot_API_search(url, param, regex):
	if param == None:
		return None
	appid="&application_id=f9f772382b14bf0bad8b14d2d5dfd852"
	result = urllib.urlopen(url + param + appid).read()
	found =  re.search(regex, result)
	if not found == None:
		return found.group(1)

def get_acc_id(playername):
	id = None
	while id == None:
		id = wot_API_search(
		"https://api.worldoftanks.eu/wot/account/list/?type=exact&search=",
		playername,
		"account_id\":([0-9]+)")
	return id

def get_clan_id(acc_id):
	return wot_API_search(
		"https://api.worldoftanks.eu/wot/account/info/?fields=clan_id&account_id=",
		acc_id,
		"clan_id\":([0-9]+)")

def get_clan_tag(clan_id):
	return wot_API_search(
		"https://api.worldoftanks.eu/wot/globalmap/claninfo/?fields=tag&clan_id=",
		clan_id,
		"clan_tag\":\"([^\"]+)")

def search_player_clan_tag(playername):
	acc_id = get_acc_id(playername)
	clan_id = get_clan_id(acc_id)
	return get_clan_tag(clan_id)
		

def add_player(dict, player, criteria):
	if player.name in dict:
		return
	if player.postcount < criteria.postcount:
		return
	clan = search_player_clan_tag(player.name)
	if not clan == None:
		if clan in criteria.clan_dict:
			return
	dict[player.name] = player

def get_players(player_dict, forum_url, max_threads, max_players, criteria):
	forum_page_count = 1
	threadcount = 0
	forum_url = options.forum_page
	name_regex = "b-author\">([^ \r\n]+)"
	postcount_regex = "post_count.+?([0-9]*,?[0-9]+)"
	nextpage_regex = "link rel='next' href='([^\']+)'"
	thread_regex="(http[^']+)' class='expander closed"

	while not forum_url == None:
		eprint("Forum Page: " + forum_url)
		forum_file = urllib.urlopen(forum_url)
		forum_page = forum_file.read()
		forum_file.close()
		threads = re.findall(thread_regex, forum_page)
		for thread in threads:
			threadcount += 1
			if (
				not max_threads == -1 and
				threadcount >= max_threads
			):
				return
			while not thread == None:
				eprint("\tThread Page: " + thread)
				topic_file = urllib.urlopen(thread)
				topic_page=topic_file.read()
				topic_file.close()
				page_names = re.findall(name_regex, topic_page)
				post_counts = re.findall(postcount_regex, topic_page, re.S)
				for name, postcount in itertools.izip(page_names, post_counts):
					add_player(	player_dict, 
								Player( name, int(postcount.translate(None, ','))), 
								criteria)
					if (
						not max_players == -1 and 
						len(player_dict) >= max_players
					):
					   return
				thread = re.findall(nextpage_regex, topic_page)
				thread = thread[0] if len(thread) > 0 else None
		forum_url = re.findall(nextpage_regex, forum_page)
		forum_url = forum_url[0] if len(forum_url) > 0 else None

op=OptionParser()
op.add_option("-f", 
			  "--forum", 
			  dest="forum_page", 
			  help="main forum page to crawl.  Optional.  Defaults to English gameplay page if left undefined", 
			  default="http://forum.worldoftanks.eu/index.php?/forum/35-gameplay/")
op.add_option("-p", 
			  "--posts", 
			  dest="posts_filter", 
			  help="minimum number of posts to classify a player as a forumite, optional, defaults to 0 if let undefined", 
			  default=0)
op.add_option("-t", 
			  "--threadcount", 
			  dest="thread_count", 
			  help="maximum number of threads to crawl, optional, default is to not set an upper bound", 
			  default=-1)
op.add_option("-n",
			  "--nickcount",
			  dest="nick_count",
			  help="maximum number of player nicknames to store, optional, default is to not set an upper bound",
			  default=-1)
(options, args) = op.parse_args()
				  
player_dict={}
clans_dict={}

with open('clans.txt') as clans:
	for line in clans:
		clans_dict[line.split(",")[0]] = line.split(",")[1]
for clan, img in clans_dict.items():
	eprint(clan + ":" + img)

get_players(player_dict, 
			options.forum_page, 
			int(options.thread_count), 
			int(options.nick_count),
			Criteria(int(options.posts_filter), clans_dict)
			)

for name in sorted(player_dict.keys()):
	print (name)
eprint(len(player_dict))
