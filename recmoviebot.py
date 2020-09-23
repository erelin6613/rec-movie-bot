#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pysnooper
from telegram import (InlineKeyboardMarkup, 
	InlineKeyboardButton, ReplyKeyboardMarkup, Poll)
from telegram.ext import (Updater, CommandHandler, 
	MessageHandler, Filters,ConversationHandler, 
	CallbackQueryHandler, BasePersistence, DictPersistence)

from scraper import *
from utils import spell_check


# Define helpers and boilerplate

d = {'typing_reply': 0, 'typing_choice': 1, 'choosing': 2}

buttons = ['Add actor', 'Add genre', 'Trending movies', 
		'Show recommendations', 'Add to watch later', 
		'Review watched', 'To the starting page', 
		'My watch list', 'Manage my preferences']

starting_buttons = [[buttons[0], buttons[1]],
					[buttons[2], buttons[3]]]

results_buttons = [[buttons[4], buttons[5]],
					[buttons[6], buttons[7]]]

help_dict = {'/top': 'Show trending movies',
			'/prefs': 'Display recorded preferences'}

start_regex = '(hi|Hi|hello|Hello|To the starting page)'


# @pysnooper.snoop()
def greet(update, context):
	"""Greeting handler. Greet a user and display starting layout."""

	markup = ReplyKeyboardMarkup(
		starting_buttons, one_time_keyboard=True)
	context.bot.send_message(chat_id=update.effective_chat.id, 
		text='I am a RecMovieBot, I can suggest you a new movies to watch.',
		reply_markup=markup)

# @pysnooper.snoop()
def display_help(update, context):
	"""Display manual for commands from help_dict"""
	markup = ReplyKeyboardMarkup(
		starting_buttons, one_time_keyboard=True)

	d = [x+':'+y for x, y in help_dict]
	d = '\n'.join(d)

	context.bot.send_message(chat_id=update.effective_chat.id, 
		text=d,
		reply_markup=markup)

# @pysnooper.snoop()
def fallback(update, context):
	"""Say bye to user."""

	markup = ReplyKeyboardMarkup(
		starting_buttons, one_time_keyboard=True)
	context.bot.send_message(chat_id=update.effective_chat.id, 
		text='See you around')

# @pysnooper.snoop()
def get_top_movies(update, context):
	"""Display popular movies in the format
	name - link. 10 movies are showed if found.
	Result is saved as bot_data to acess
	when needed."""

	markup = ReplyKeyboardMarkup(
		results_buttons, one_time_keyboard=True)

	movies = get_listing_items()
	#m = '\n'.join([k+' - '+v for k, v in movies.items()])
	m = '\n'.join(['{}. {} - {}'.format(
		i+1, k, movies[k]) for i, k in enumerate(movies)])
	context.bot_data['last_recomendation'] = movies 

	context.bot.send_message(
		chat_id=update.effective_chat.id, 
		text=m,
		reply_markup=markup)

# @pysnooper.snoop()
def basic_recommendations(update, context):
	"""Display basic recommendation based on the
	user's favourite genre or actor. Tell the user
	we know nothing about him/her to recommend
	anything if there is no data."""

	markup = ReplyKeyboardMarkup(
		results_buttons, one_time_keyboard=True)

	if 'genre' in list(context.user_data.keys()):
		genre = context.user_data['genre'][0]
		genre = spell_check(genre)
		movies = scrape_by_genre(genre)
		m = '\n'.join(['{}. {} - {}'.format(
			i+1, k, movies[k]) for i, k in enumerate(movies)])
		#m = '\n'.join([k+' - '+v for k, v in movies.items()])
		context.bot_data['last_recomendation'] = movies 
		context.bot.send_message(
			chat_id=update.effective_chat.id, 
			text=m,
			reply_markup=markup)

	elif 'actor' in list(context.user_data.keys()):
		actor = context.user_data['actor'][0]
		movies = scrape_by_cast(actor)
		#m = '\n'.join([k+' - '+v for k, v in movies.items()])
		m = '\n'.join(['{}. {} - {}'.format(
			i+1, k, movies[k]) for i, k in enumerate(movies)])
		context.bot_data['last_recomendation'] = movies 
		context.bot.send_message(
			chat_id=update.effective_chat.id, 
			text=m,
			reply_markup=markup)

	else:
		context.bot.send_message(
			chat_id=update.effective_chat.id, 
			text='I do not think I have a data to recommend you something')

# @pysnooper.snoop()
def show_users_prefs(update, context):
	"""Display data bot collected about the user"""

	prefs = str(context.user_data)
	context.bot.send_message(
		chat_id=update.effective_chat.id, 
		text=str(context.user_data))

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
	markup = ReplyKeyboardMarkup(
		starting_buttons, one_time_keyboard=True)
	try:
		category = user_data['choice']
		try:
			assert len(user_data[category]) != 0
			user_data[category].append(text)
		except Exception:
			user_data[category] = [text]
		del user_data['choice']

		update.message.reply_text(
			"Neat! I added that to your preferences.",
			reply_markup=markup)
	except Exception as e:
		update.message.reply_text(
			"Did you choose something? I caught a hiccup")
		print(e)

	return d['choosing']

# @pysnooper.snoop()
def add_to_watchlist(update, context):
	"""Store the bulk of movies to the 
	watch_list. At this point bot adds
	all the movies it found just a
	step before."""

	markup = ReplyKeyboardMarkup(
		starting_buttons, one_time_keyboard=True)
	movies = context.bot_data['last_recomendation']
	movies_buttons = [x for x in movies.keys()]
	markup_choice = ReplyKeyboardMarkup(
		movies_buttons, one_time_keyboard=True)

	try:
		assert len(context.user_data['watch_list']) != 0
	except Exception:
		context.user_data['watch_list'] = {}

	for k, v in movies.items():
		context.user_data['watch_list'][k] = v
	update.message.reply_text(
		"Cool! {} movies added to your watch later list.".format(
			len(movies)), markup=markup)

# @pysnooper.snoop()
def display_watch_list(update, context):
	"""Display movies from watch_list in the 
	format name - link."""
	markup = ReplyKeyboardMarkup(
		starting_buttons, one_time_keyboard=True)
	movies = context.user_data['watch_list']
	m = '\n'.join([k+' - '+v for k, v in movies.items()])
	context.bot_data['last_recomendation'] = movies 
	context.bot.send_message(
		chat_id=update.effective_chat.id, 
		text=m,
		reply_markup=markup)

# @pysnooper.snoop()
def main(production=False):

	updater = Updater(os.environ.get('api_key'), 
		use_context=True)
	dp = updater.dispatcher

	greet_handler = MessageHandler(
			(Filters.regex(start_regex) & 
			(~Filters.command)), greet)

	prefs_handler = CommandHandler('prefs', show_users_prefs)
	help_handler = CommandHandler('help', show_users_prefs)

	typing_reply_handler = MessageHandler(
		(Filters.regex('{}|{}'.format(buttons[0], buttons[1]))),
		regular_choice)
	typing_choice_handler = MessageHandler(
		(Filters.text) & (~Filters.command) & (~Filters.regex(
			'|'.join([x for x in buttons]))), 
		received_information)

	top_movies_handler = MessageHandler(
		(Filters.regex(buttons[2])), get_top_movies)
	basic_rec_handler = MessageHandler(
		(Filters.regex(buttons[3])), basic_recommendations)

	watch_list_add_handler = MessageHandler(
		(Filters.regex(buttons[4])), add_to_watchlist)
	display_list_add_handler = MessageHandler(
		(Filters.regex(buttons[7])), display_watch_list)

	f_handler = MessageHandler((Filters.regex('bye')), fallback)

	dp.add_handler(prefs_handler)
	dp.add_handler(help_handler)
	dp.add_handler(greet_handler)
	dp.add_handler(typing_reply_handler)
	dp.add_handler(typing_choice_handler)
	dp.add_handler(top_movies_handler)
	dp.add_handler(basic_rec_handler)
	dp.add_handler(watch_list_add_handler)
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
	main(production=False)