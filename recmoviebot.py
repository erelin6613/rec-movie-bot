#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import html
import json
import pysnooper
import logging
import traceback
from collections import OrderedDict
from telegram import (InlineKeyboardMarkup, 
	InlineKeyboardButton, ReplyKeyboardMarkup, Poll, Sticker)
from telegram.ext import (Updater, CommandHandler, 
	MessageHandler, Filters,ConversationHandler, 
	CallbackQueryHandler, DictPersistence)

from text_correction import fix_sentence
from utils import get_vocab
from moviebase import MovieBase


logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
	level=logging.INFO)

logger = logging.getLogger(__name__)

d = {'typing_reply': 0, 'typing_choice': 1, 'choosing': 2}

screens = OrderedDict({'start': 100,
			'how_work': 101,
			'add_genre': 102,
			'trending':103,
			'recs': 104,
			'add_wl': 105,
			'review': 106,
			'my_wl': 107,
			'showing_prefs':108,
			'showing_help': 109,
			'my_profile': 110,
			'back': 111,
			'my_prefs': 112})

screen_texts, screen_nums = list(
	screens.keys()), list(screens.values())
# print(screens, screen_texts, screen_nums)

buttons = ['How does it work?', 'Add genre', 'Top rated...', 
		'Show recommendations', 'Add to watch later', 
		'Add favourite movie', 'To the starting page', 
		'My watch list', 'Manage my preferences',
		'Add actor',
		'Trending', 'By genre', 'By actor']

starting_buttons = [[buttons[5], buttons[1]],
					[buttons[2], buttons[3]]]

results_buttons = [[buttons[4], buttons[5]],
					[buttons[6], buttons[7]]]

add_pref_buttons = [[buttons[1], buttons[-4]],
					[buttons[6], buttons[7]]]

help_dict = {'/top': 'Show trending movies',
			'/prefs': 'Display recorded preferences',
			'/about': 'Information about RecMovieBot'}

start_regex = '(hi|Hi|hello|Hello|To the starting page)(\s|$)'


def error_handler(update, context):
	"""Log the error and send a telegram message to notify the developer."""
	# Log the error before we do anything else, so we can see it even if something breaks.
	logger.error(msg="Exception while handling an update:", exc_info=context.error)

	# traceback.format_exception returns the usual python message about an exception, but as a
	# list of strings rather than a single string, so we have to join them together.
	tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
	tb = ''.join(tb_list)

	# Build the message with some markup and additional information about what happened.
	# You might need to add some logic to deal with messages longer than the 4096 character limit.
	message = (
		'An exception was raised while handling an update\n'
		'update = {}\n\n'
		'context.chat_data = {}\n\n'
		'context.user_data = {}\n\n'
		'{}'
	).format(
		html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
		html.escape(str(context.chat_data)),
		html.escape(str(context.user_data)),
		html.escape(tb),
	)

	print(message)

	# Finally, send the message
	#context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)

# @pysnooper.snoop()
def greet(update, context):
	"""Greeting handler. Greet a user and display starting layout."""

	if 'moviebase' not in context.bot_data.keys():
		context.bot_data['moviebase'] = MovieBase()
	markup = ReplyKeyboardMarkup(
		starting_buttons, 
		one_time_keyboard=True,
		resize_keyboard=True)
	update.message.reply_text(
		text='I am a RecMovieBot, I can suggest you a new movies to watch.',
		reply_markup=markup)

	return d['choosing']

# @pysnooper.snoop()
def display_help(update, context):
	"""Display manual for commands from help_dict"""
	markup = ReplyKeyboardMarkup(
		starting_buttons, one_time_keyboard=True)

	d = [x+': '+y for x, y in help_dict.items()]
	d = '\n'.join(d)

	context.bot.send_message(chat_id=update.effective_chat.id, 
		text=d,
		reply_markup=markup)
	return screens['showing_help']

# @pysnooper.snoop()
def fallback(update, context):
	"""Say bye to user."""

	markup = ReplyKeyboardMarkup(
		starting_buttons, 
		one_time_keyboard=True, 
		resize_keyboard=True)
	context.bot.send_message(chat_id=update.effective_chat.id, 
		text='See you around')

def explain(update, context):
	explain_file = os.path.dirname(__file__)
	explain_file = os.path.join(explain_file, 'knowledge_base', 'explain.txt')
	with open(explain_file) as f:
		text = f.read()
	context.bot.send_message(chat_id=update.effective_chat.id, 
		text=text)

def show_trending(update, context):
	
	markup = ReplyKeyboardMarkup(
		[[buttons[-3], buttons[-2], buttons[-1]]], 
		one_time_keyboard=True,
		resize_keyboard=True)
	message = 'What is that you want?'
	context.bot.send_message(
		chat_id=update.effective_chat.id, 
		text=message,
		reply_markup=markup)
	#print(update.message.text)
	return screens['my_wl']


#@pysnooper.snoop()
def get_top_movies(update, context):
	"""Display popular movies in the format
	name - link. 10 movies are showed if found.
	Result is saved as bot_data to acess
	when needed."""

	if 'moviebase' not in context.bot_data.keys():
		context.bot_data['moviebase'] = MovieBase()

	markup = ReplyKeyboardMarkup(
		results_buttons, 
		one_time_keyboard=True,
		resize_keyboard=True)

	by = update.message.text
	movies = None

	if by != buttons[-3]:
		by = by.split(' ')[-1]

		if by=='genre' and 'genre' in context.user_data.keys():
			movies = context.bot_data['moviebase'].get_top_rated(genre=context.user_data['genre'])
		elif by=='actor' and 'actor' in context.user_data.keys():
			movies = context.bot_data['moviebase'].get_top_rated(actor=context.user_data['actor'])
		else:
			markup = ReplyKeyboardMarkup(
				add_pref_buttons, 
				one_time_keyboard=True,
				resize_keyboard=True)
			text = 'Please add your favourite {} first'.format(by)
			context.bot.send_message(
				chat_id=update.effective_chat.id, 
				text=text,
				reply_markup=markup)
			return screens['my_wl']

	if movies is None:			
		movies = context.bot_data['moviebase'].get_top_rated()

	message = ''
	for i, mId in enumerate(movies.index):
		message = message+str(
			i+1)+'. '+movies.loc[mId, 'title']+' - '+movies.loc[mId, 'imdbUrl']+'\n'
	context.bot_data['last_recomendation'] = movies

	if message == '':
		message = 'Ouch, I think I do not know onces you tagged'

	context.bot.send_message(
		chat_id=update.effective_chat.id, 
		text=message,
		reply_markup=markup)

	return screens['my_wl']

def review_movie(update, context):

	context.user_data['choice'] = 'reviewed'
	update.message.reply_text(
		'What movie did you like? Type the name of it, will see if I know it')

	return d['typing_reply']

def one_to_watchlist(update, context):

	context.user_data['choice'] = 'watch_list'
	update.message.reply_text(
		'What movie should I add there? Type the name of it and I will add it')

	return d['typing_reply']

def smart_recommendations(update, context):

	markup = ReplyKeyboardMarkup(
		results_buttons, 
		one_time_keyboard=True,
		resize_keyboard=True)

	if 'reviewed' in context.user_data.keys():
		context.bot.send_message(
			chat_id=update.effective_chat.id, 
			text='Searching best movies ...',
			reply_markup=markup)

		titles = context.user_data['reviewed']
		movies = context.bot_data['moviebase'].get_by_reviewed(titles)
	elif 'genre' in context.user_data.keys():
		#print('goes to algo', context.user_data['genre'])
		movies = context.bot_data['moviebase'].get_top_rated(
			genre=context.user_data['genre'])

	else:
		context.bot.send_message(
			chat_id=update.effective_chat.id, 
			text='Ehm, I do not know anything you like? Want to review a movie?',
			reply_markup=markup)
		return screens['my_wl']
	message = ''
	for i, mId in enumerate(movies.index):
		message = message+str(
			i+1)+'. '+movies.loc[mId, 'title']+' - '+movies.loc[mId, 'imdbUrl']+'\n'
	context.bot_data['last_recomendation'] = movies 

	context.bot.send_message(
		chat_id=update.effective_chat.id, 
		text=message,
		reply_markup=markup)

	return screens['my_wl']

def show_users_prefs(update, context):
	"""Display data bot collected about the user"""

	prefs = str(context.user_data)
	context.bot.send_message(
		chat_id=update.effective_chat.id, 
		text=str(context.user_data))
	return screens['showing_prefs']

# @pysnooper.snoop()
def regular_choice(update, context):
	"""Given a choice user made store it in
	the user_data dictionary to use it later."""

	text = update.message.text.split(' ')[-1]
	context.user_data['choice'] = text
	update.message.reply_text(
		'Your favourite {}? Sure, go ahead and type it!'.format(
			text.lower()))

	return d['typing_reply']

# @pysnooper.snoop()
def received_information(update, context):
	"""Store user's preferences."""
	user_data = context.user_data
	text = update.message.text
	if 'moviebase' not in context.bot_data.keys():
		context.bot_data['moviebase'] = MovieBase()

	try:
		print(user_data)
		category = user_data['choice']
		if category == 'reviewed':
			markup = ReplyKeyboardMarkup(
				starting_buttons, 
				one_time_keyboard=True,
				resize_keyboard=True)

			movie = context.bot_data['moviebase'].lookup_movie(text)

			if movie is None:
				message = 'I do not know this one, sorry :('
				context.user_data['reviewed'].pop(title)
			else:
				movie_title, movie_url = movie[0], movie[1]
				message = "Ah, this one {} Okay, I noted it.".format(movie_url)

			update.message.reply_text(
				message,
				reply_markup=markup)
			try:
				assert len(user_data[category]) != 0
				user_data[category].append(movie_title)
			except Exception:
				user_data[category] = [movie_title]
			print(user_data)
			del user_data['choice']

			return d['choosing']

		elif category == 'watch_list':
			markup = ReplyKeyboardMarkup(
				results_buttons, 
				one_time_keyboard=True,
				resize_keyboard=True)
			movie = context.bot_data['moviebase'].lookup_movie(text)

			if movie is None:
				message = 'I do not know this one, sorry :('
				# context.user_data['reviewed'].pop(title)
			else:
				movie_title, movie_url = movie[0], movie[1]
				message = "Great! {} is added to your watchlist.".format(movie_title)

			update.message.reply_text(
				message,
				reply_markup=markup)
			try:
				assert len(user_data[category]) != 0
				user_data[category].append(movie_title)
			except Exception:
				user_data[category] = [movie_title]
			#print(user_data)
			del user_data['choice']

			return d['choosing']

		try:
			assert len(user_data[category]) != 0
			user_data[category].append(text)
		except Exception as e:
			#print(e)
			user_data[category] = [text]
		del user_data['choice']
		markup = ReplyKeyboardMarkup(
			starting_buttons, 
			one_time_keyboard=True,
			resize_keyboard=True)

		update.message.reply_text(
			"Neat! I added that to your preferences.",
			reply_markup=markup)
	except Exception as e:
		update.message.reply_text(
			"Please specify the command first")
		#print(e)

	return d['choosing']


def get_list_choice(update, context):

	context.user_data['list_choice'] = context.callback_query.data #int(num)-1
	#return 

# @pysnooper.snoop()
def add_to_watchlist(update, context):
	"""Store the bulk of movies to the 
	watch_list. At this point bot adds
	all the movies it found just a
	step before."""

	markup = ReplyKeyboardMarkup(
		starting_buttons, 
		one_time_keyboard=True,
		resize_keyboard=True)
	movies = context.bot_data['last_recomendation']
	#print(movies)
	movies_buttons = [[x] for x in movies.keys()]
	markup_choice = ReplyKeyboardMarkup(
		movies_buttons, 
		one_time_keyboard=True,
		resize_keyboard=True)

	try:
		assert len(context.user_data['watch_list']) != 0
	except Exception:
		context.user_data['watch_list'] = {}
	print(context.chat_data)

	for k, v in movies.items():
		context.user_data['watch_list'][k] = v
	update.message.reply_text(
		"Cool! {} movies added to your watch later list.".format(
			len(movies)), markup=markup)

# @pysnooper.snoop()
def display_watch_list(update, context):
	"""Display movies from watch_list in the 
	format name - link."""
	if 'moviebase' not in context.bot_data.keys():
		context.bot_data['moviebase'] = MovieBase()
	markup = ReplyKeyboardMarkup(
		starting_buttons, 
		one_time_keyboard=True,
		resize_keyboard=True)

	try:
		assert len(context.user_data['watch_list']) != 0
	except Exception:
		update.message.reply_text(
			"You do not have any movies here yet.",
			markup=markup)
		return d['choosing']

	movies = context.user_data['watch_list']
	titles = movies #['title']
	links = context.bot_data['moviebase'].dataset #movies['imdbUrl']
	
	#print(links[links.title==titles[0]]['imdbUrl'])
	links = [links[links.title==x]['imdbUrl'].values[0] for x in titles]
	#print(movies)
	m = '\n'.join([movie+' - '+link for movie, link in zip(titles, links)])
	#context.bot_data['last_recomendation'] = movies 
	context.bot.send_message(
		chat_id=update.effective_chat.id, 
		text=m,
		reply_markup=markup)

#@pysnooper.snoop()
def main(production=False):

	updater = Updater(os.environ.get('api_key'), 
		use_context=True)
	dp = updater.dispatcher

	greet_handler = MessageHandler(
			(Filters.regex(start_regex) & 
			(~Filters.command)), greet)

	prefs_handler = CommandHandler('prefs', show_users_prefs)
	help_handler = CommandHandler('help', display_help)
	start_handler = CommandHandler('start', greet)
	about_handler = CommandHandler('about', explain)

	typing_reply_handler = MessageHandler(
		(Filters.regex('{}|{}'.format(buttons[1], buttons[-4]))),
		regular_choice)
	review_movie_handler = MessageHandler(
		(Filters.regex('{}'.format(buttons[5]))),
		review_movie)
	one_to_watchlist_handler = MessageHandler(
		(Filters.regex('{}'.format(buttons[4]))),
		one_to_watchlist)
	typing_choice_handler = MessageHandler(
		(Filters.text) & (~Filters.command) & (~Filters.regex(
			'|'.join([x for x in buttons]))), 
		received_information)

	choice_movies_handler = MessageHandler(
		(Filters.regex(buttons[2])), show_trending)

	top_movies_handler = MessageHandler(
		(Filters.regex('{}|{}|{}'.format(buttons[-3], buttons[-2], buttons[-1]))), get_top_movies)
	recommendation_handler = MessageHandler(
		(Filters.regex(buttons[3])), smart_recommendations)

	#watch_list_add_handler = MessageHandler(
	#	(Filters.regex(buttons[4])), add_to_watchlist)
	display_list_add_handler = MessageHandler(
		(Filters.regex(buttons[7])), display_watch_list)

	#list_choice_handler = CallbackQueryHandler(get_list_choice, pattern='[0-9]')
	f_handler = MessageHandler((Filters.regex('bye')), fallback)

	dp.add_handler(prefs_handler)
	dp.add_handler(help_handler)
	dp.add_handler(about_handler)
	dp.add_handler(greet_handler)
	dp.add_handler(review_movie_handler)
	dp.add_handler(choice_movies_handler)
	#dp.add_handler(list_choice_handler)
	dp.add_handler(typing_reply_handler)
	dp.add_handler(typing_choice_handler)
	dp.add_handler(top_movies_handler)
	dp.add_handler(recommendation_handler)
	dp.add_handler(one_to_watchlist_handler)
	dp.add_handler(display_list_add_handler)
	
	dp.add_handler(f_handler)

	if production:
		updater.start_webhook(listen='0.0.0.0',
								port=int(os.environ.get('PORT')),
								url_path=os.environ.get('api_key'))
		updater.bot.setWebhook(
			"https://recmoviebot.herokuapp.com/{}".format(
				os.environ.get('api_key')))
	updater.start_polling()
	updater.idle()


if __name__ == '__main__':
	main(production=True)