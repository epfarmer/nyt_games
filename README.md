# NYT Games

These lil babies can help you solve the New York Times games Wordle and Spelling Bee.

## Prerequisites

Python modules:

- [requests](https://requests.readthedocs.io/en/latest/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [nltk](https://www.nltk.org/)
- [sklearn](https://scikit-learn.org/stable/)
- [wordfreq](https://github.com/rspeer/wordfreq/)

## Usage

### Wordlebot

From a command line, run `wordlebot.py`. Enter your guess, followed by the color of the tiles: (g)reen, (y)ellow, or (b)lack. For instance, for the following guess:

![Wordle guess](https://i.imgur.com/qSW327L.png)

one would enter `arose`, followed by `byygg`.

Wordlebot will start by suggesting words with the highest character frequency in the wordbank. After the first guess, it will consider word frequency as well, and after the third guess it will no longer consider character frequency.

### Spelling Bee Bot

From a command line, run `spelling_bee_bot.py`. Enter the key letter, followed by the remaining letters. For instance, for the following game:

![Spelling bee](https://i.imgur.com/tfeLo1H.png)

one would enter `l`, followed by `iorcfm`.

Additionally, one may enter `w` or `f` to look up potential solutions in the [Webster](https://www.merriam-webster.com/) or [Free](https://dictionaryapi.dev/) dictionaries, respectively. If one chooses to use the Webster dictionary for word lookups, one will need to acquire an API key [here](https://dictionaryapi.com/), and define it in a `.env` file as `WEBSTER_API_KEY`.

## License

[MIT](https://choosealicense.com/licenses/mit/)
