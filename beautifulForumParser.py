#!/usr/bin/python3
'''
beautifulForumParser.py

Remake of the original forumcrawler, written from scratch, and using BeautifulSoup for sanity and
code simplication.  Most notably, I removed the regular expression based parsing (see
http://stackoverflow.com/questions/1732348/regex-match-open-tags-except-xhtml-self-contained-tags#1732454
for more details.
The code now no longer needs to even look at the WG API...  which I only needed to hit before to 
get information that I couldn't get without being bothered to write stupidly complex regular expressions 
before.  BeautifulSoup lets me collect all that without having to drill deeper.  Success!

This is horribly horribly 'IO' bound, and it doesn't even stress the networking capabilities either.
It's just a lot of waiting.
We need threads, lots of threads
<img href="http://ic.pics.livejournal.com/voxaudita/46493925/7383/7383_600.jpg" alt="no, this isn't my image">
'''
from optparse import OptionParser
from bs4 import BeautifulSoup
import requests
import collections
import time

def parseOptions():
  op=OptionParser()
  op.add_option("-d",
          "--debug",
          default="",
          help="whatever debug options exist at this time")
  op.add_option("-f", 
          "--forum", 
          dest="forum_page", 
          help="main forum page to crawl.  Optional.  Defaults to English gameplay page if left undefined", 
          default="http://forum.worldoftanks.eu/index.php?/forum/35-gameplay/")
  op.add_option("-i", 
          "--ignore_clan", 
          dest="clan_list", 
          help="space separated list of clans to ignore (if they are well known as forumites (e.g. dingers) then we let them keep their clan logo", 
          default="")
  op.add_option("-m", 
          "--min-posts", 
          dest="posts_filter", 
          help="minimum number of posts to classify a player as a forumite, optional, defaults to 100 if let undefined", 
          default=100)
  op.add_option("-o",
          "--output_file",
          dest="output_file",
          help="filename where namelist will be saved",
          default="namelist.csv")
  op.add_option("-p", 
          "--pages", 
          dest="page_count", 
          help="target number of pages of threads to crawl, optional, default is to not set an upper bound", 
          default=-1)
  op.add_option("-n",
          "--nickcount",
          dest="nick_count",
          help="target number of player nicknames to store, optional, default is to not set an upper bound.  Note: this is total unique names scanned, output name list may not be this long",
          default=-1)
  (options, args) = op.parse_args()
  options.clan_list = options.clan_list.split(' ')
  options.nick_count = int(options.nick_count)
  options.page_count = int(options.page_count)
  if len(options.debug):
    with open(options.debug, 'w') as outfile:
      outfile.write('')
  return options

def get_next_page(soup):
  try:
    next_page = soup.find(title='Next page').get('href')
    return next_page
  except:
    return None
    
def make_soup(link):
  #try for a minute then return whatever we have
  for i in range(30):
    try:
      page = requests.get(link, timeout=10)
      return BeautifulSoup(page.text, 'html.parser')
    except:
      print(f'requests timeout {i}')
      pass   

def hrefs_from_page(link):
  soup = make_soup(link)
  link_generator = (a.get('href') for a in soup('a', class_='expander closed'))
  next_page = get_next_page(soup)
  return (link_generator, next_page)
  
def player_valid(player):
  global options
  return player['clan']not in options.clan_list and player['posts'] > options.posts_filter
  
  
def player_name(post_soup):
  name = post_soup.find('span', class_='author vcard b-author b-author').text.strip()
  return name
  
def player_clan(post_soup):
  try:
    return next( i for i in post_soup('a') if i.get('rel',[''])[0]=='home').text
  except:
    return None

def player_posts(post_soup):
  number = (  post_soup.find('li', class_='post_count desc lighter margin-bottom')
        .find('span', class_='row_data').text.replace(',', ''))
  return int(number)
    

def players_from_page(link, nameD):
  max_str_len = 0
  print('')
  while link:
    if len(topic) > max_str_len:
      max_str_len = len(topic) + 1
    print (f'\r{link}'.ljust(max_str_len), end="")
    soup = make_soup(link)
    for post in soup('div', class_='post_wrap'):
      player = {}
      player['name' ] = player_name (post)
      player['clan' ] = player_clan (post)
      player['posts'] = player_posts(post)
      if player['name'] not in nameD and player_valid(player):
        nameD[player['name']] = player
        debug_output(player)
    link = get_next_page(soup)

def output_data(data, filename):
  global options
  with open(filename, 'w') as outfile:
  #this should be made to use csvwriter properly at some point.
  #too tired to do it now, so hacky way it is...
    '''
    writer = csv.DictWriter(outfile, fieldnames=['name','clan','posts'])
    writer.writeheader()
    writer.writerows(sorted(nameD.items()))
    '''
    outfile.write('name,clan,posts')
    for k,v in sorted(nameD.items()):
      outfile.write('{},{},{}\n'.format(v['name'], v['clan'], v['posts']))
      
def debug_output(data):
  global options
  if len(options.debug):
    with open(options.debug, 'a') as outfile:
      outfile.write('{},{},{}\n'.format(data['name'], data['clan'], data['posts']))
  
options = parseOptions()
if options.nick_count < 0 and options.page_count < 0:
  print("please set an upper bound.  See the help prompt for more information on how to use this program")
  exit

nameD = collections.defaultdict()
page_count = 0
page = options.forum_page

while ( page and 
    ( page_count < options.page_count or 
      len(nameD) < options.nick_count)):
  page_count += 1
  topics, page = hrefs_from_page(page)
  for topic in topics:
    players_from_page(topic, nameD)
  
output_data(nameD, options.output_file)


