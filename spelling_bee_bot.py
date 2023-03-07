import json
import os
from collections import defaultdict
from os import getenv
from pathlib import Path

import requests as req
from dotenv import load_dotenv
from nltk.corpus import words
from wordfreq import zipf_frequency

load_dotenv()
wordle_folder = os.path.dirname(__file__)


class SpellingBeeBot:
    def __init__(self):

        self.load_wordbank()

    def load_wordbank(self):
        wordbank_file = "spelling_bee_bank.json"
        wordbank_path = Path(os.path.dirname(__file__)) / wordbank_file

        if not wordbank_path.is_file():
            self.generate_wordbank(wordbank_path)

        with open(wordbank_path) as f:
            self.wordbank: dict[str:float] = json.load(f)

    def generate_wordbank(self, wordbank_path):

        print(f"creating wordbank file")

        wordlist: dict[str:float] = {
            w: freq
            for w in sorted(set(words.words()))
            if all((len(w) >= 4, w.islower(), freq := zipf_frequency(w, "en")))
        }

        with open(wordbank_path, "w", encoding="utf-8") as f:
            json.dump(
                wordlist,
                f,
                indent=4,
                sort_keys=True,
            )

    def get_definitions(self, lookup: str) -> None:
        lookup_dict = {
            "w": self.webster_lookup,
            "f": self.freedict_lookup,
        }
        self.words = [w for w in self.words if lookup_dict[lookup](w)]

    def webster_lookup(self, word: str) -> bool:
        webster_url = "https://dictionaryapi.com/api/v3/references/collegiate/json"
        res = req.get(f"{webster_url}/{word}?key={getenv('WEBSTER_API_KEY')}")
        res_json = res.json()[0]
        if type(res_json) != str:
            definitions = " -- ".join(res_json["shortdef"])
            print(f"{word}: {definitions}")
            return True
        return False

    def freedict_lookup(self, word: str) -> bool:
        res = req.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
        if res.status_code == 200:
            definition = res.json()[0]["meanings"][0]["definitions"][0]["definition"]
            print(f"{word}: {definition}")
            return True
        return False

    def get_words(self) -> None:

        self.available_letters = set(self.key + self.letters)

        self.words = {
            word: freq
            for word, freq in self.wordbank.items()
            if self.key in word and all([c in self.available_letters for c in word])
        }

    def report_words(self) -> None:
        words_collection = defaultdict(list)
        for word in self.words:
            words_collection[len(word)].append(word)
        for length, words in sorted(words_collection.items()):
            print(f"{length} letter words: {', '.join(words)}")

        pangrams = [
            word
            for word in self.words
            if all([letter in word for letter in self.available_letters])
        ]
        print(f"PANGRAMS: {', '.join(pangrams)}")

    def start(self):
        while True:
            try:
                self.key = input("enter key letter: ").lower()
                if len(self.key) != 1 or not self.key.isalpha():
                    raise ValueError
                break
            except ValueError:
                print("key must be one letter")

        while True:
            try:
                self.letters = input("enter 6 surrounding letters: ").lower()
                if len(self.letters) != 6 or not self.letters.isalpha():
                    raise ValueError
                break
            except ValueError:
                print("must enter 6 surrounding letters")

        while True:
            try:
                lookup = input(
                    "(w)ebster or (f)ree dictionary (blank to skip): "
                ).lower()
                if not len(lookup):
                    lookup = None
                    break
                if len(lookup) > 1 or not set("wf").issuperset(lookup):
                    raise ValueError
                break
            except ValueError:
                print(
                    'enter "w" for webster or "f" for free dictionary (blank to skip)'
                )

        self.get_words()
        if lookup:
            self.get_definitions(lookup)
        self.report_words()


def main():
    spelling_bee_bot = SpellingBeeBot()
    spelling_bee_bot.start()


if __name__ == "__main__":
    main()
