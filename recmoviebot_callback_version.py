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
	InlineKeyboardButton, ReplyKeyboardMarkup, Poll)
from telegram.ext import (Updater, CommandHandler, 
	MessageHandler, Filters,ConversationHandler, 
	CallbackQueryHandler, DictPersistence)

from scraper import *
from text_correction import fix_sentence
from utils import get_vocab


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define helpers and boilerplate

d = {'typing_reply': 0, 'typing_choice': 1, 'choosing': 2}

screens = OrderedDict({'start': 100,
			'add_actor': 101,
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

	buttons = [[
		#InlineKeyboardButton(text='Add an actor', callback_data=str(actor_choice)),
		#InlineKeyboardButton(text=screen_texts[0], callback_data=str(regular_choice)),
		InlineKeyboardButton(text=screen_texts[3], callback_data=str(screens['trending'])),
		InlineKeyboardButton(text=screen_texts[10], callback_data=str(screens['my_profile']))

	]]
	keyboard = InlineKeyboardMarkup(buttons)
	#print(update.callback_query)
	#update.callback_query.answer()
	update.message.reply_text(
		text='I am a RecMovieBot, I can suggest you a new movies to watch.',
		reply_markup=keyboard)
	"""
	markup = ReplyKeyboardMarkup(
		starting_buttons, one_time_keyboard=True)
	context.bot.send_message(chat_id=update.effective_chat.id, 
		text='I am a RecMovieBot, I can suggest you a new movies to watch.',
		reply_markup=markup)
	"""
	return d['choosing']

@pysnooper.snoop()
def show_profile(update, context):
	"""Greeting handler. Greet a user and display starting layout."""

	buttons = [[
		#InlineKeyboardButton(text='Add an actor', callback_data=str(actor_choice)),
		#InlineKeyboardButton(text=screen_texts[0], callback_data=str(regular_choice)),
		InlineKeyboardButton(text=screen_texts[1], callback_data=str(screens['add_actor'])),
		InlineKeyboardButton(text=screen_texts[2], callback_data=str(screens['add_genre']))],
		[InlineKeyboardButton(text=screen_texts[12], callback_data=str(screens['my_prefs'])),
		InlineKeyboardButton(text=screen_texts[11], callback_data=str(screens['back']))

	]]
	keyboard = InlineKeyboardMarkup(buttons)
	#print(update.callback_query)
	#update.callback_query.answer()
	text = 'okay, here is your profile dashboard'
	update.callback_query.answer()
	print('show_profile called')
	update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
	"""
	markup = ReplyKeyboardMarkup(
		starting_buttons, one_time_keyboard=True)
	context.bot.send_message(chat_id=update.effective_chat.id, 
		text='I am a RecMovieBot, I can suggest you a new movies to watch.',
		reply_markup=markup)
	"""
	return d['typing_choice']

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
	return screens['showing_help']

# @pysnooper.snoop()
def fallback(update, context):
	"""Say bye to user."""

	markup = ReplyKeyboardMarkup(
		starting_buttons, one_time_keyboard=True)
	context.bot.send_message(chat_id=update.effective_chat.id, 
		text='See you around')

@pysnooper.snoop()
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

	return screens['my_wl']

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
		genre = fix_sentence(genre)
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

	return screens['my_wl']

# @pysnooper.snoop()
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

	ind = int(update.callback_query.data) % 100
	vocab_name = screen_texts[ind].split('_')[-1]
	data = get_vocab(vocab_name)[:8]
	#context.user_data['choice'] = text
	buttons = [
		[InlineKeyboardButton(text=data[x], callback_data=str(150+x)) for x in range(2)],
		[InlineKeyboardButton(text=data[x+2], callback_data=str(152+x)) for x in range(2)],
		[InlineKeyboardButton(text=data[x+4], callback_data=str(154+x)) for x in range(2)],
		[InlineKeyboardButton(text=data[x+6], callback_data=str(156+x)) for x in range(2)]
	]
	keyboard = InlineKeyboardMarkup(buttons)
	text = 'Here are the most popular {} people look for'.format(vocab_name)
	update.callback_query.answer()
	update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

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


def get_list_choice(update, context):
	#update.message.reply_text('')
	#num = update.message.text

	context.user_data['list_choice'] = context.callback_query.data #int(num)-1
	#return 

def add_item(update, context):
	pass

# @pysnooper.snoop()
def add_to_watchlist(update, context):
	"""Store the bulk of movies to the 
	watch_list. At this point bot adds
	all the movies it found just a
	step before."""

	markup = ReplyKeyboardMarkup(
		starting_buttons, one_time_keyboard=True)
	movies = context.bot_data['last_recomendation']
	movies_buttons = [[x] for x in movies.keys()]
	markup_choice = ReplyKeyboardMarkup(
		movies_buttons, one_time_keyboard=True)

	try:
		assert len(context.user_data['watch_list']) != 0
	except Exception:
		context.user_data['watch_list'] = {}
	#print(context.user_data['watch_list'])
	#print(movies)
	#choice = context.user_data['list_choice']
	#context.user_data['watch_list'][movies_buttons[choice]] = list(movies.values())[choice]
	#context.user_data['list_choice'] = None
	#update.message.reply_text('Which one?')
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
	markup = ReplyKeyboardMarkup(
		starting_buttons, one_time_keyboard=True)

	try:
		assert len(context.user_data['watch_list']) != 0
	except Exception:
		update.message.reply_text(
			"You do not have any movies here yet.",
			markup=markup)
		return d['choosing']

	movies = context.user_data['watch_list']
	m = '\n'.join([k+' - '+v for k, v in movies.items()])
	context.bot_data['last_recomendation'] = movies 
	context.bot.send_message(
		chat_id=update.effective_chat.id, 
		text=m,
		reply_markup=markup)

@pysnooper.snoop()
def main(production=False):

	updater = Updater(os.environ.get('api_key'), 
		use_context=True)
	dp = updater.dispatcher

	#greet_handler = MessageHandler(
	#		(Filters.regex(start_regex) & 
	#		(~Filters.command)), greet)

	prefs_handler = CommandHandler('prefs', show_users_prefs)
	help_handler = CommandHandler('help', show_users_prefs)
	start_handler = CommandHandler('start', greet)

	greet_handler = CallbackQueryHandler(
		CallbackQueryHandler, pattern='hi')

	top_movies_handler = CallbackQueryHandler(
		get_top_movies, pattern=str(screens['trending']))
	profile_handler = CallbackQueryHandler(
		show_profile, pattern=str(screens['my_profile']))

	add_actor_handler = CallbackQueryHandler(
		regular_choice, pattern=str(screens['add_actor']))
	add_genre_handler = CallbackQueryHandler(
		regular_choice, pattern=str(screens['add_genre']))
	back_handler = CallbackQueryHandler(
		# for now we will return just to starting screen
		greet, pattern=str(screens['start']))

	#screen_choice_handler = CallbackQueryHandler(regular_choice, pattern=str())
	"""
	top_movies_handler = CallbackQueryHandler(
		get_top_movies, pattern=str(screens['trending']))
	basic_rec_handler = CallbackQueryHandler(
		basic_recommendations, pattern=str(screens['recs']))
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


	#list_choice_handler = MessageHandler(Filters.regex('[0-9]'), get_list_choice)
	list_choice_handler = CallbackQueryHandler(get_list_choice, pattern='[0-9]')
	f_handler = MessageHandler((Filters.regex('bye')), fallback)

	dp.add_handler(prefs_handler)
	dp.add_handler(help_handler)
	dp.add_handler(greet_handler)
	dp.add_handler(list_choice_handler)
	dp.add_handler(typing_reply_handler)
	dp.add_handler(typing_choice_handler)
	dp.add_handler(top_movies_handler)
	dp.add_handler(basic_rec_handler)
	dp.add_handler(watch_list_add_handler)
	dp.add_handler(display_list_add_handler)
	dp.add_handler(f_handler)
	"""

	dp.add_handler(prefs_handler)
	dp.add_handler(help_handler)
	dp.add_handler(start_handler)
	dp.add_handler(top_movies_handler)
	dp.add_handler(profile_handler)
	dp.add_handler(add_actor_handler)
	dp.add_handler(add_genre_handler)
	dp.add_handler(back_handler)
	#dp.add_handler(basic_rec_handler)
	dp.add_error_handler(error_handler)

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