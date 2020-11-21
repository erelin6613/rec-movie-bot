import os
import numpy as np
from nltk import edit_distance, jaccard_distance, word_tokenize
import argparse
import sys
import re

def define_paths(root_dir):

	vocabs = {'genre': os.path.join(
				root_dir, 'knowledge_base', 'genre.txt')
			}

	return vocabs

def get_vocab(label):

	root_dir = os.path.dirname(__file__)

	vocabs = define_paths(root_dir)
	with open(vocabs[label]) as f:
		vocab = f.read().split('\n')
	return vocab

def get_candidate(word, vocab, jaccard_thresh=0.4):
	min_d = 10
	candidate = word
	if word.isdigit():
		return word
	for w in vocab:
		d = edit_distance(w, word.lower())
		if d < min_d:
			if d > 2 and len(word)>5:
				continue
			if d > 1 and len(word)<=5:
				continue
			j_distance = jaccard_distance(set(candidate), set(word.lower()))
			if j_distance < jaccard_thresh:
				min_d = d
				candidate = w

	return candidate

def fix_sentence(sentence, label):
	vocab = get_vocab(label)
	sentence = clean_str(sentence)
	sentence = remove_junk(sentence)
	if ' ' in sentence:
		tokens = sentence.split(' ')
	else:
		tokens = [sentence]
	tokens = [x for x in tokens if len(x) != 0]
	result = []

	for t in tokens:
		if t.lower() in vocab:
			result.append(t)
			continue
		result.append(get_candidate(t, vocab))
	return ' '.join(result)

def remove_junk(string):
	junk = '%^*\'|/?"():'
	for ch in junk:
		string = string.replace(ch, '')
	return string

def clean_str(text):
	"""Method dedicated to remove extra spaces
	and unwanted characters in the string.

	@param: string - string to be cleaned

	@return: string - the same string with extra
			spaces removed
	"""

	text = re.sub(r'(\n|\r|\t)', ' ', text)
	text = ''.join([x for x in text if x.isprintable()])
	text = re.sub(r' +', ' ', text)
	
	if text.startswith(' '):
		text = text[1:]
	if text.endswith(' '):
		text = text[:-1]
	return text