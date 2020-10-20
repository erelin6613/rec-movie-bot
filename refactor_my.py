#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pysnooper
from telegram import (InlineKeyboardMarkup, 
	InlineKeyboardButton, ReplyKeyboardMarkup, Poll)
from telegram.ext import (Updater, CommandHandler, 
	MessageHandler, Filters,ConversationHandler, 
	CallbackQueryHandler, DictPersistence)

from scraper import *
from utils import spell_check

states = {'select_action': 2,
		'add_feature': 3,
		'showing_list': 4,
		'asking_input': 5,
		'adding_to_watchlist': 6,
		'selecting_movie': 7,
		'profile_menu': 8,
		'controling_list': 9,
		'show_actors': 10,
		'start_over': 11,
		'back': 12,
		'typing_reply':13,
		'save_input': 14
		}

choices = {'actors': 100,
		'genres': 101,
		'movies': 102}

end_level = ConversationHandler.END

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


@pysnooper.snoop()
def greet(update, context):
	"""Greeting handler. Greet a user and display starting layout."""

	markup = ReplyKeyboardMarkup(
		starting_buttons, one_time_keyboard=True)
	context.bot.send_message(chat_id=update.effective_chat.id, 
		text='I am a RecMovieBot, I can suggest you a new movies to watch.',
		reply_markup=markup)

	return states['select_action']

@pysnooper.snoop()
def profile_menu(update, context):
	#text = 'check'
	buttons = [[
		InlineKeyboardButton(text='My genres', callback_data=str(states['show_actors'])),
		InlineKeyboardButton(text='My actors', callback_data=str(states['show_actors']))
	], [
		InlineKeyboardButton(text='My movies', callback_data=str(states['show_actors'])),
		#InlineKeyboardButton(text='Show data', callback_data=str(SHOWING)),
		InlineKeyboardButton(text='Back', callback_data=str(end_level))
	]]
	keyboard = InlineKeyboardMarkup(buttons)

	# If we're starting over we don't need do send a new message
	if context.user_data.get(states['start_over']):
		text = 'What\' next?'
		update.callback_query.answer()
		update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
	else:
		text = 'Hi, I\'m MovieRecBot.'
		update.message.reply_text(text=text, reply_markup=keyboard)

	context.user_data[states['start_over']] = False
	#print(context.args)
	#print(states['select_action'])
	return states['select_action']

@pysnooper.snoop()
def display_help(update, context):
	"""Display manual for commands from help_dict"""
	markup = ReplyKeyboardMarkup(
		starting_buttons, one_time_keyboard=True)

	d = [x+':'+y for x, y in help_dict]
	d = '\n'.join(d)

	context.bot.send_message(chat_id=update.effective_chat.id, 
		text=d,
		reply_markup=markup)

@pysnooper.snoop()
def fallback(update, context):
	"""Say bye to user."""

	markup = ReplyKeyboardMarkup(
		starting_buttons, one_time_keyboard=True)
	context.bot.send_message(chat_id=update.effective_chat.id, 
		text='See you around')
	return end_level

def stop(update, context):
	"""End Conversation by command."""
	update.message.reply_text('Okay, bye.')

	return end_level

@pysnooper.snoop()
def show_actors(update, context):

	#ud = context.user_data
	try:
		assert len(context.user_data['actors']) > 0
		text, memory = item_format(context.user_data['actors'])
	except Exception:
		#string, memory = item_format(ud['actors'])
		text, memory = 'I do not think you told me that.', None
	context.user_data['choice'] = 'actors'

	buttons = [[
		#InlineKeyboardButton(text='Add an actor', callback_data=str(actor_choice)),
		InlineKeyboardButton(text='Back', callback_data=str(end_level))
	]]
	keyboard = InlineKeyboardMarkup(buttons)

	update.callback_query.answer()
	text = text+'\n\nType an actor name to add it to the list.'
	update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
	#ud[START_OVER] = True

	return states['typing_reply']

def add_actor(update, context):
	print('checking message handler')
	try:
		context.user_data['actors'].append(update.message.text)
	except Exception as e:
		print(e)
		context.user_data['actors'] = [update.message.text]
	buttons = [[
		#InlineKeyboardButton(text='Add an actor', callback_data=str(actor_choice)),
		InlineKeyboardButton(text='Back', callback_data=str(end_level))
	]]
	keyboard = InlineKeyboardMarkup(buttons)
	update.message.reply_text('Okay, I will remember you like {}'.format(update.message.text), reply_markup=keyboard)

	return received_information(update, context)


def show_genres(update, context):

	#ud = context.user_data
	try:
		assert len(context.user_data['genre']) > 0
		text, memory = item_format(context.user_data['genre'])
	except Exception:
		#string, memory = item_format(ud['actors'])
		text, memory = 'I do not think you told me that.', None
	context.user_data['choice'] = 'genre'

	buttons = [[
		InlineKeyboardButton(text='Add an genre', callback_data=str(actor_choice)),
		InlineKeyboardButton(text='Back', callback_data=str(end_level))
	]]
	keyboard = InlineKeyboardMarkup(buttons)

	update.callback_query.answer()
	update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
	#ud[START_OVER] = True

	return states['typing_reply']


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

@pysnooper.snoop()
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

	elif 'actors' in list(context.user_data.keys()):
		actor = context.user_data['actors'][0]
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

@pysnooper.snoop()
def show_users_prefs(update, context):
	"""Display data bot collected about the user"""

	prefs = str(context.user_data)
	context.bot.send_message(
		chat_id=update.effective_chat.id, 
		text=str(context.user_data))

@pysnooper.snoop()
def actor_choice(update, context):
	"""Given a choice user made store it in
	the user_data dictionary to use it later."""

	#update.callback_query.edit_message_text(
		#'Your favourite actor? Sure, go ahead and type it!')
	#help(update)
	print('actor_choice called')
	update.message.reply_text('Who is that?')
	try:
		context.user_data['actors'].append(text)
	except Exception:
		context.user_data['actors'] = text

	return states['show_actors']

@pysnooper.snoop()
def received_information(update, context):
	"""Store user's preferences."""
	user_data = context.user_data
	text = update.message.text
	print('--------received_information called')
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
			"Neat! I added that to your preferences.")
	except Exception as e:
		update.message.reply_text(
			"Did you choose something? I caught a hiccup")
		print(e)

	context.bot.send_message(
				chat_id=update.effective_chat.id, 
				text='I do not think I have a data to recommend you something')

	return states['back']

@pysnooper.snoop()
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

	for k, v in movies.items():
		context.user_data['watch_list'][k] = v
	update.message.reply_text(
		"Cool! {} movies added to your watch later list.".format(
			len(movies)), markup=markup)

@pysnooper.snoop()
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
def end_level(update, context):
	"""Return to top level conversation."""
	context.user_data[states['start_over']] = True
	profile_menu(update, context)

	return end_level

def start_test(update, context):
	buttons = [[
		#InlineKeyboardButton(text='Add an actor', callback_data=str(actor_choice)),
		InlineKeyboardButton(text='test', callback_data=str(end_level))
	]]
	keyboard = InlineKeyboardMarkup(buttons)
	update.callback_query.answer()
	update.callback_query.edit_message_text(text='test666', reply_markup=keyboard)

	return 333

def print_666(update, context):
	update.callback_query.answer()
	update.callback_query.edit_message_text(text='666', reply_markup=keyboard)
	return 777

def print_777(update, context):
	update.callback_query.answer()
	update.callback_query.edit_message_text(text='777', reply_markup=keyboard)
	return 666


def main(production=False):

	updater = Updater(os.environ.get('api_key'), 
		use_context=True)
	dp = updater.dispatcher

	main_handler = ConversationHandler(
		entry_points=[CommandHandler('start', profile_menu)],

		states = {
			states['profile_menu']: [CallbackQueryHandler(
				profile_menu, pattern=str(states['profile_menu']))],

			states['show_actors']: [CallbackQueryHandler(
				show_actors, pattern=str(states['show_actors']))],

			states['select_action']: [CallbackQueryHandler(
				show_actors, pattern=r'\d+')],

			states['back']: [CallbackQueryHandler(
				end_level, pattern=str(end_level))],
			
			states['typing_reply']: [MessageHandler(~Filters.command, 
				add_actor)],

			states['save_input']: [CallbackQueryHandler(
				received_information, pattern=str(states['save_input']))]
				#, pattern='^'+str(states['typing_reply'])+'$')]
			},

		fallbacks=[CallbackQueryHandler(
				end_level, pattern='^'+str(end_level)+'$')]
		)

	"""

	profile_handler = ConversationHandler(
		entry_points=[CallbackQueryHandler(select_feature,
										   pattern='^' + str(MALE) + '$|^' + str(FEMALE) + '$')],

		states={
			SELECTING_FEATURE: [CallbackQueryHandler(ask_for_input,
													 pattern='^(?!' + str(END) + ').*$')],
			TYPING: [MessageHandler(Filters.text & ~Filters.command, save_input)],
		},

		fallbacks=[
			CallbackQueryHandler(end_describing, pattern='^' + str(END) + '$'),
			CommandHandler('stop', stop_nested)
		],

		map_to_parent={
			END: SELECTING_LEVEL,
			STOPPING: STOPPING,
		}
	)
	"""

	test_handler = ConversationHandler(
		entry_points = [CommandHandler('start', start_test)],
		states = {
			666: [CallbackQueryHandler(print_666,
				pattern=str(666))],
			777: [CallbackQueryHandler(print_777,
				pattern=str(777))],
		},
		fallbacks=[CallbackQueryHandler(
				end_level)]
		)

	prefs_handler = CommandHandler('prefs', show_users_prefs)
	help_handler = CommandHandler('help', show_users_prefs)

	dp.add_handler(main_handler)

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