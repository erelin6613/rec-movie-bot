import os
import sys
from nltk.metrics import edit_distance

def define_paths(root_dir):

	vocabs = {'genre': os.path.join(
				root_dir, 'knowledge_base', 'genre.txt'),
			'actor': os.path.join(
				root_dir, 'knowledge_base', 'actor.txt')
			}

	return vocabs

def item_format(data, key):
	memory = enumerate(data)
	if isinstance(dict, data[key]):
		s = '\n'.join(['{}. {} - {}'.format(
			i+1, k, data[key]) for i, k in memory])
	else:
		s = '\n'.join(['{}. {}'.format(
			i+1, k) for i, k in memory])

	return s, memory

def split_list (l, x):
	return [l[i:i+x] for i in range(0, len(l), x)]

def get_genres():
	vocab = get_vocab('genre')
	return vocab

def get_vocab(label):

	root_dir = os.path.dirname(__file__)

	vocabs = define_paths(root_dir)
	with open(vocabs[label]) as f:
		vocab = f.read().split('\n')
	return vocab