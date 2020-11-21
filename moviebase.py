import os
import sys
import json
import math
import numpy as np
import pandas as pd
import nltk
import re
from sklearn.metrics.pairwise import pairwise_distances
import pysnooper

dataset_dir = os.path.join(
	os.path.dirname(__file__), 'movielens_latest')

title_baselink = 'https://www.imdb.com/title/tt'

class MovieBase:

	def __init__(self, dataset_dir=dataset_dir,
		dataset_name='small_set_movies',
		storage_format='csv',
		rec_df_name='rec_vec_df'):

		filename = os.path.join(
			dataset_dir, dataset_name+'.'+storage_format)

		if storage_format == 'csv':
			self.dataset = pd.read_csv(filename)
		elif storage_format == 'json':
			self.dataset = pd.read_json(filename)
		if rec_df_name is not None:
			self.rec_df = pd.read_csv(os.path.join(dataset_dir, rec_df_name+'.'+storage_format))

		self.dataset.loc[:, 'imdbUrl'] = self.dataset['imdbId'].astype(str)
		self.dataset.loc[:, 'imdbUrl'] = self.dataset['imdbUrl'].apply(pad_to_len)
		self.dataset.loc[:, 'imdbUrl'] = self.dataset['imdbUrl'].apply(lambda x: title_baselink+x)

		self.rec_df = pd.read_csv(os.path.join(dataset_dir, 'rec_df_small'+'.'+storage_format))

	def __len__(self):
		return len(self.dataset)

	def _build_title_vocab(self):
		vocab = []

	def _build_user_matrix(self, movies=None, ratings=None, userId=7777):
		n_items = self.rec_df['movieId'].unique().shape[0]
		user_matrix = np.zeros((1, n_items))
		if movie is None:
			pass
		else:
			for movie, rate in zip(movies, rating):
				pass
				#movie, rating = 
		#vec = pd.DataFrame({'userId': })


	def get_movie_genres(self, idx):
		genres = self.dataset.loc[idx, 'genres'].split('|')
		return genres

	def get_imdb_link(self, idx):
		link = self.dataset.loc[idx, 'imdbId']
		return title_baselink+link

	def get_records(self, idx, columns=['title', 'imdbId']):
		return self.dataset.loc[idx, columns]

	def list_genres(self):
		genres = self.dataset.genres.apply(
			lambda x: x.split('|') if '|' in x else [x])
		genres_set = set()
		for g in genres:
			for each in g:
				genres_set.add(each)
		genres_set.remove('(no genres listed)')
		return list(genres_set)

	def get_top_rated(self, num=10, genre=None, actor=None):

		if genre is None:
			top = self.dataset.sort_values('median_rate')[-num:]
		elif genre is not None:
			genres = self.list_genres()
			top = pd.DataFrame()
			while len(top)<num:
				for genre in genres:
					top_by_genre = self.dataset[self.dataset['genres'].str.contains(
						genre.capitalize())].sort_values('median_rate') #[self.dataset.index[-1]]
					if len(top_by_genre)!=0:
						top_by_genre = top_by_genre.loc[top_by_genre.index[-1], :]
						top = top.append(top_by_genre, ignore_index=True)
		if len(top)>num:
			return top.loc[top.index[:num], :]
		return top

	@pysnooper.snoop()
	def get_by_reviewed(self, reviewed, num=10):

		recs = self.rec_df.pivot_table(index ='userId', columns ='title', values ='rating')
		recommended_df = pd.DataFrame()

		while len(recommended_df)<num:

			for movie in reviewed:
				recommendation = recs.corrwith(recs[movie])
				recommendation = recommendation.dropna().sort_values(ascending = False).index[:num]
				recommendation = self.dataset[self.dataset['title'].isin(recommendation)]
				recommended_df = recommended_df.append(recommendation, ignore_index=True)
				recommended_df = recommended_df[~recommended_df['title'].isin(reviewed)]
				recommended_df = recommended_df.drop_duplicates(subset=['title'], keep='first')
				#print(recommended_df.columns)
			break

		pred = recommended_df.sort_values(by=['median_rate'], ascending = False)[:num]
		print(pred[['title', 'median_rate']])

		return pred


	def lookup_movie(self, query, by='title'):

		movie = self.dataset[self.dataset[by].str.contains(
			query, regex=False, case=False)]

		return movie['title'].values[0], movie['imdbUrl'].values[0], movie['imdbId'].values[0]

def pad_to_len(value, length=7):
    value = str(value)
    while len(value)<length:
        value = '0'+value
    return value