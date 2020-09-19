import requests
from bs4 import BeautifulSoup

imdb_url = 'https://www.imdb.com'
item_class = 'lister-item-content'

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

def get_listing_items(num_items=10):
	text = get_link('chart/moviemeter')
	#print(text)
	soup = BeautifulSoup(text, 'lxml')
	items = {}
	n = 0
	for m in soup.find_all('a'):
		if n == num_items:
			break
		try:
			if '/title/tt' in m.get('href'):
				#print(m.get_text())
				name = m.text.strip()
				link = imdb_url+m.get('href')
				if len(name) == 0:
					continue
				items[name] = link
				n += 1
		except Exception as e:
			#print(m)
			pass
	#items = [x.text for x in soup.find_all('a') if 'title' in x.get('href')]
	return items

def get_link(extension=None):
	if extension is None:
		r = requests.get(imdb_url)
	else:
		r = requests.get(imdb_url+'/'+extension)
	return r.text

# print(get_listing_items())