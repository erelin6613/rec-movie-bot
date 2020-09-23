import os
from nltk.metrics import edit_distance

imdb_genres = ['comedy', 'sci-fi', 'horror', 
			'romance', 'action', 'thriller', 
			'drama', 'mystery', 'crime',
			'animation', 'adventure',
			'fantasy', 'comedy,romance',
			'action,comedy', 'western', 'war',
			'sport', 'biography', 'film-noir']

def spell_check(word):
	"""Check the word based on edit distance"""
	word = word.lower()
	distances = {}
	for w in imdb_genres:
		d = edit_distance(word, w)
		if d==0:
			return word
		distances[w] = d
	min_d = min(list(distances.values()))
	candidates = [k for k, v in distances.items() if v==min_d]
	return candidates[0]