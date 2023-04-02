import json
import os
from collections import defaultdict
from pathlib import Path

from wordfreq import zipf_frequency


class SpellingBeeBot:
    def __init__(self):

        wordbank_folder = Path(os.path.dirname(__file__))
        self.dictionary_file = wordbank_folder / "webster_dictionary.json"
        self.wordbank_file = wordbank_folder / "spelling_bee_bank.json"

        if not self.wordbank_file.is_file():
            self.generate_wordbank()

        with open(self.wordbank_file) as f:
            self.wordbank: dict[str:float] = json.load(f)

        self.start()

    def generate_wordbank(self):

        print(f"creating wordbank file")

        with open(self.dictionary_file) as f:
            wordbank: dict[str:str] = json.load(f)

        wordlist: dict[str:float] = {
            w: d for w, d in wordbank.items() if len(w) >= 4 and zipf_frequency(w, "en")
        }

        with open(self.wordbank_file, "w", encoding="utf-8") as f:
            json.dump(wordlist, f, indent=4, sort_keys=True, ensure_ascii=False)

    def get_words(self, definitions: bool = True) -> None:

        self.words = {
            w: d
            for w, d in self.wordbank.items()
            if self.key in w and self.check_word(w)
        }

        if definitions:
            for w, d in self.words.items():
                first_def = d.split("\n")[0]
                print(f"{w}: \n{first_def}\n")

        words_collection = defaultdict(list)
        for word in self.words:
            words_collection[len(word)].append(word)
        for length, words in sorted(words_collection.items()):
            print(f"{length} letter words: {', '.join(words)}")

        pangrams = [w for w in self.words if self.check_pangram(w)]
        print(f"PANGRAMS: {', '.join(pangrams)}")

    def check_word(self, word):
        for c in word:
            if c not in self.available_letters:
                return False
        return True

    def check_pangram(self, word):
        for c in self.available_letters:
            if c not in word:
                return False
        return True

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
                other_letters = input("enter 6 surrounding letters: ").lower()
                if len(other_letters) != 6 or not other_letters.isalpha():
                    raise ValueError
                self.available_letters = set(self.key + other_letters)
                break
            except ValueError:
                print("must enter 6 surrounding letters")

        self.get_words()


def main():
    SpellingBeeBot()


if __name__ == "__main__":
    main()
