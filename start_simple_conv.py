#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os

from telegram import (ReplyKeyboardMarkup, InlineKeyboardMarkup, 
	InlineKeyboardButton, ReplyKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
													ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
										level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [['Age', 'Favourite colour'],
									['Number of siblings', 'Something else...'],
									['Done']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data):
		facts = list()

		for key, value in user_data.items():
				facts.append('{} - {}'.format(key, value))

		return "\n".join(facts).join(['\n', '\n'])


def start(update, context):
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

	#context.user_data[states['start_over']] = False

	return CHOOSING


def regular_choice(update, context):
		text = update.message.text
		context.user_data['choice'] = text
		update.message.reply_text(
				'Your {}? Yes, I would love to hear about that!'.format(text.lower()))

		return TYPING_REPLY


def custom_choice(update, context):
		update.message.reply_text('Alright, please send me the category first, '
															'for example "Most impressive skill"')

		return TYPING_CHOICE


def received_information(update, context):
		user_data = context.user_data
		text = update.message.text
		category = user_data['choice']
		user_data[category] = text
		del user_data['choice']

		update.message.reply_text("Neat! Just so you know, this is what you already told me:"
															"{} You can tell me more, or change your opinion"
															" on something.".format(facts_to_str(user_data)),
															reply_markup=markup)

		return CHOOSING


def done(update, context):
		user_data = context.user_data
		if 'choice' in user_data:
				del user_data['choice']

		update.message.reply_text("I learned these facts about you:"
															"{}"
															"Until next time!".format(facts_to_str(user_data)))

		user_data.clear()
		return ConversationHandler.END


def main():
		# Create the Updater and pass it your bot's token.
		# Make sure to set use_context=True to use the new context based callbacks
		# Post version 12 this will no longer be necessary
		updater = Updater(os.environ.get('api_key'), use_context=True)

		# Get the dispatcher to register handlers
		dp = updater.dispatcher

		# Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
		conv_handler = ConversationHandler(
				entry_points=[CommandHandler('start', start)],

				states={
						CHOOSING: [MessageHandler(Filters.regex('^(Age|Favourite colour|Number of siblings)$'),
																			regular_choice),
											 MessageHandler(Filters.regex('^Something else...$'),
																			custom_choice)
											 ],

						TYPING_CHOICE: [
								MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')),
															 regular_choice)],

						TYPING_REPLY: [
								MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')),
															 received_information)],
				},

				fallbacks=[MessageHandler(Filters.regex('^Done$'), done)]
		)

		dp.add_handler(conv_handler)

		# Start the Bot
		updater.start_polling()

		# Run the bot until you press Ctrl-C or the process receives SIGINT,
		# SIGTERM or SIGABRT. This should be used most of the time, since
		# start_polling() is non-blocking and will stop the bot gracefully.
		updater.idle()


if __name__ == '__main__':
		main()