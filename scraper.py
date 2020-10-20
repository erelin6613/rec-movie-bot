import requests
import pysnooper
from bs4 import BeautifulSoup
from collections import OrderedDict

imdb_url = 'https://www.imdb.com'
item_class = 'lister-item-content'

# @pysnooper.snoop()
def search_list(soup, num_items=10, op=None):
	"""Basic function to collect links to movies.
	Note: the only distinction of the search here
	is of the interface of IMDB with respect to
	actor, we want to collect the movies from 
	`known for` section (at least for now)"""
	items = {}
	n = 0
	if op=='actor':
		s = soup.find_all('a', class_='knownfor-ellipsis')
	else:
		s = soup.find_all('a')
	for m in s:
		if len(items) == num_items:
			break
		try:
			if '/title/tt' in m.get('href'):
				name = m.text.strip()
				link = imdb_url+m.get('href')
				if len(name) == 0:
					continue
				items[name] = link
				n += 1
		except Exception as e:
			pass
	return items

# @pysnooper.snoop()
def scrape_by_genre(key_word):
	"""Colect movie names and links based on genre"""
	link = imdb_url+f'/search/title/?genres={key_word}'
	r = requests.get(link)
	soup = BeautifulSoup(r.text, 'lxml')
	items = search_list(soup)
	return items

# @pysnooper.snoop()
def scrape_by_cast(person):
	"""Colect movie names and links based on actor"""
	link = imdb_url+f'/find?q={person}'
	r = requests.get(link)
	soup = BeautifulSoup(r.text, 'lxml')
	actors = soup.find_all('a')
	actor_link = None
	for a in actors:
		try:
			if '/name/nm' in a.get('href'):
				actor_link = imdb_url+a.get('href')
				break
		except Exception as e:
			pass
	if actor_link is None:
		return None
	r = requests.get(actor_link)
	soup = BeautifulSoup(r.text, 'lxml')
	items = search_list(soup)
	return items

# @pysnooper.snoop()
def get_listing_items(num_items=5):
	"""Colect movie names and links for popular ones"""
	text = get_link('chart/moviemeter')
	soup = BeautifulSoup(text, 'lxml')
	items = search_list(soup)
	return OrderedDict(items)

# @pysnooper.snoop()
def get_link(extension=None):
	"""Get response from the base imdb url,
	appends extension if applicable"""
	if extension is None:
		r = requests.get(imdb_url)
	else:
		r = requests.get(imdb_url+'/'+extension)
	return r.text