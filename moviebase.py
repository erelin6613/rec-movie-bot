import os
import sys
import json
import math
import numpy as np
import pandas as pd
import nltk
import re
from sklearn.metrics.pairwise import cosine_similarity
import pysnooper

dataset_dir = os.path.join(
	os.path.dirname(__file__), 'movielens_latest')

title_baselink = 'https://www.imdb.com/title/tt'

class MovieBase:

	def __init__(self, query_csv='query_df.csv'):

		self.dataset = pd.read_csv(query_csv)
		self.__init_matrix()

	def __init_matrix(self):
		self.mapping = pd.Series(
			self.dataset.reset_index().index, index = self.dataset.title)
		X = self.dataset.genres.str.split(',', expand=True)[0]
		X = pd.get_dummies(X)
		X_reg = pd.get_dummies(self.dataset.region)
		X = pd.concat([X, X_reg], axis=1)
		X = pd.concat([X, self.dataset.startYear/2020], axis=1)
		X = pd.concat([X, self.dataset.averageRating/10], axis=1)
		X = pd.concat([X, self.dataset.isAdult], axis=1)
		X = pd.concat(
			[X, self.dataset.runtimeMinutes/self.dataset.runtimeMinutes.max()],
			axis=1)
		self.similarity_matrix = cosine_similarity(X, X)

	def get_top_rated(self, genre=None, actor=None, num=10):
		if genre is not None:
			top = pd.DataFrame()
			for g in genre:
				g_df = self.dataset[self.dataset.genres.str.contains(
					g, regex=False, case=False)]
				top = top.append(g_df, ignore_index=True)
			top = top.sort_values('averageRating')[-num:]

		elif actor is not None:
			top = pd.DataFrame()
			for g in actor:
				g_df = self.dataset[self.dataset.actors.str.contains(
					g, regex=False, case=False)]
				top = top.append(g_df, ignore_index=True)
			top = top.sort_values('averageRating')[-num:]

		else:
			top = self.dataset.sort_values('averageRating')[-num:]
		if len(top)>num:
			return top.loc[top.index[:num], :]
		return top

	def get_by_reviewed(self, reviewed, num=10):

		recommended_df = pd.DataFrame()

		movies_per_rev = round(num/len(reviewed))+1

		while len(recommended_df)<num:

			for movie in reviewed:
				movie_index = self.mapping[movie]
				similarity_score = list(enumerate(self.similarity_matrix[movie_index]))
				similarity_score = sorted(similarity_score, key=lambda x: x[1], reverse=True)
				similarity_score = similarity_score[1:movies_per_rev]
				movie_indices = [i[0] for i in similarity_score]
				print(self.dataset.iloc[movie_indices])
				recommended_df = recommended_df.append(self.dataset.iloc[movie_indices], ignore_index=True)
			break

		pred = recommended_df.sort_values(by=['averageRating'], ascending = False)[:num]
		#print(pred[['title', 'median_rate']])

		return pred

	def lookup_movie(self, query, by='title'):

		movie = self.dataset[self.dataset[by].str.contains(
			query, regex=False, case=False)]

		return movie['title'].values[0], movie['imdbUrl'].values[0]