import requests
from bs4 import BeautifulSoup

imdb_url = 'https://www.imdb.com'

def scrape_by_kw(key_word, choice='pop'):
	if choice == 'pop':
		link = imdb_url+'/chart/top'
	elif choice == 'genre':
		link = imdb_url+f'/search/title/?genres={key_word}'
	r = requests.get(link)
	soup = BeautifulSoup(r.text)
	l = soup.find(class_='lister')
	l = [x.text for x in l.findall('a')]
	return l.text