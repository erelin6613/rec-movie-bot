#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pysnooper
from telegram import (InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, 
	MessageHandler, Filters,ConversationHandler, CallbackQueryHandler)

from scraper import get_listing_items

d = {'typing_reply': 0, 'typing_choice': 1, 'choosing': 2}
starting_buttons = [['Add actor', 'Add genre'],
					['Trending movies', 'Show recommendations']]

help_dict = {'/top': 'Show trending movies',
			'/prefs': 'Display recorded preferences'}

storage = {}
storage['actor'] = []
storage['genre'] = []

@pysnooper.snoop()
def greet(update, context):
	markup = ReplyKeyboardMarkup(starting_buttons, one_time_keyboard=True)
	context.bot.send_message(chat_id=update.effective_chat.id, 
		text='I am a RecMovieBot, I can suggest you a new movies to watch.',
		reply_markup=markup)

@pysnooper.snoop()
def display_help(update, context):
	markup = ReplyKeyboardMarkup(starting_buttons, one_time_keyboard=True)
	d = [x+':'+y for x, y in help_dict]
	d = '\n'.join(d)
	context.bot.send_message(chat_id=update.effective_chat.id, 
		text=d,
		reply_markup=markup)

@pysnooper.snoop()
def fallback(update, context):
	markup = ReplyKeyboardMarkup(starting_buttons, one_time_keyboard=True)
	context.bot.send_message(chat_id=update.effective_chat.id, 
		text='See you around')

@pysnooper.snoop()
def get_top_movies(update, context):
	movies = get_listing_items()
	movies = '\n'.join([k+' - '+v for k, v in movies.items()])
	context.bot.send_message(chat_id=update.effective_chat.id, 
		text=movies)

@pysnooper.snoop()
def show_users_prefs(update, context):
	prefs = str(context.user_data)
	context.bot.send_message(chat_id=update.effective_chat.id, 
		text=prefs)

@pysnooper.snoop()
def regular_choice(update, context):
	#print(update, context)
	text = update.message.text.split(' ')[-1]
	context.user_data['choice'] = text
	update.message.reply_text(
		'Your favourite {}? Yes, I would love to hear about that!'.format(text.lower()))

	return d['typing_reply']

@pysnooper.snoop()
def received_information(update, context):
	user_data = context.user_data
	text = update.message.text
	try:
		category = user_data['choice']
		user_data[category] = text
		storage[category].append(text)

		update.message.reply_text("Neat! Just so you know, this is what you already told me:"
			"{} You can tell me more, or change your opinion"
			" on something.".format(str(storage)))
	except Exception as e:
		update.message.reply_text("Did you choose something? I caught a hiccup")
		print(e)

	return d['choosing']


def main(production=False):

	#storage = init_storage()

	updater = Updater(os.environ.get('api_key'), use_context=True)
	dp = updater.dispatcher

	greet_handler = MessageHandler(
			(Filters.regex('(hi|Hi|hello|Hello)') & 
			(~Filters.command)), greet)

	#link_handler = CommandHandler('top', get_top_movies)
	prefs_handler = CommandHandler('prefs', show_users_prefs)
	help_handler = CommandHandler('help', show_users_prefs)

	typing_reply_handler = MessageHandler(
		(Filters.regex('Add genre|Add actor')), regular_choice)
	typing_choice_handler = MessageHandler(
		(Filters.text) & (~Filters.command) & (~Filters.regex('Trending movies')), 
		received_information)
	top_movies_handler = MessageHandler(
		(Filters.regex('Trending movies')), get_top_movies)
	f_handler = MessageHandler((Filters.regex('bye')), fallback)

	dp.add_handler(prefs_handler)
	dp.add_handler(help_handler)
	dp.add_handler(greet_handler)
	dp.add_handler(typing_reply_handler)
	dp.add_handler(typing_choice_handler)
	dp.add_handler(top_movies_handler)
	dp.add_handler(f_handler)
	#dp.add_handler(conv_handler)

	if production:
		updater.start_webhook(listen='0.0.0.0',
								port=int(os.environ.get('PORT')),
								url_path=os.environ.get('api_key'))
		updater.bot.setWebhook(
			"https://recmoviebot.herokuapp.com/{}".format(os.environ.get('api_key')))
	updater.start_polling()
	updater.idle()


if __name__ == '__main__':
	main(production=True)