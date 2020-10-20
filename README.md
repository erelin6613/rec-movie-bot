### General algorythm behind the bot

Bot relies on interactive user experience and its actions are triggered with text input. Once it is greeted RecMovieBot gives a user a few options. The buttons will help a user to choose needed action. Current version allows use to:

- to see the most popular movies *Trending movies*
- add favourite actors *Add actor*
- add favourite genre *Add genre*
- show basic recommendations based on prevoiusly entered actor or genre

### Data storage

As the hosting is taken care of with heroku, the task of data storage become not practical without external data storage systems. RecMovieBot will remember your favourites but only within a session.

### IMDB data

To provide a list of movies under the hood RecMovieBot uses IMDB website.
P.S. It is a simple request to IMDB website, depending on call parameter it is scraping either a front page or a corresponding search. Given sufficient time it would be ideal to use IMDB API.

### Telegram intergation

Mainly program is integrated with Python package [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot), high-level wrapper package around telegram bot API.

### Program language and dependencies

RecMovieBot is written purely in Python. There are a few dependencies specified in `requirements.txt` of which are important to highlight:

* python-telegram-bot - core library for telegram bot commands and calls execution
* nltk - natural language processing package (as of current version used for spell checking for genres input)
* requests - library for url response handling
* BeautifulSoup - parsing tool for HTML response handling

### Core functions

Note: the main files where code is executed are recmoviebot.py, text_correction.py, scraper.py and utils.py. Other files contain experimental code helping levedge education around telegram API, state handling, etc.

* main - logic for handlers defenition and excecution
* greet - function for handling bots starting state
* display_help
* get_top_movies - triggers the call to get trending movies
* basic_recommendations - handles the data arrgregation for displaying recommendations (as of now the first input of genre is used for baseline recommendations, if not inputed by user, input of actor is used insead, message telling user the bot has no reference data otherwise)
* add_to_watchlist - logic behind adding movies to user's watch list (as of now adds a bulk of movies which were shown user the last, and will be lost ater the session)