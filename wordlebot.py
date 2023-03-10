import json
import os
from collections import Counter, namedtuple
from operator import attrgetter
from pathlib import Path

from nltk.corpus import words
from sklearn.preprocessing import minmax_scale
from wordfreq import zipf_frequency


class WordleBot:
    def __init__(self):

        self.Word = namedtuple("Word", ["word", "word_freq", "char_freq"])
        self.Letter = namedtuple("Letter", ["pos", "char", "color"])
        self.Suggestion = namedtuple("Suggestion", ["word", "weight"])

        self.load_wordbank()
        self.guesses = 6
        self.make_suggestion()

    def load_wordbank(self) -> None:
        wordbank_file = "wordle_bank.json"
        wordbank_path = Path(os.path.dirname(__file__)) / wordbank_file

        if not wordbank_path.is_file():
            self.generate_wordbank(wordbank_path)

        with open(wordbank_path) as f:
            self.wordbank = [
                self.Word(w["word"], w["word_freq"], w["char_freq"])
                for w in json.load(f)
            ]
            self.max_words = len(self.wordbank)

    def generate_wordbank(self, wordbank_path) -> None:

        print(f"creating wordbank file")

        wordlist: list[str] = [
            w for w in sorted(set(words.words())) if len(w) == 5 and w.islower()
        ]
        word_freq = {
            word: freq for word in wordlist if (freq := zipf_frequency(word, "en"))
        }
        scaled_word_freq = {
            word: freq
            for word, freq in zip(
                word_freq, minmax_scale([w for w in word_freq.values()])
            )
        }

        letters = Counter()
        for word in wordlist:
            letters.update(word)
        total = sum([v for v in letters.values()])
        letter_freq = {k: v / total for k, v in letters.items()}
        # takes the sum of the set of letter frequencies in the wordlist and divides by 5
        # this penalizes words with duplicate letters
        char_freq = {
            word: sum([letter_freq[c] for c in set(word)]) / 5 for word in word_freq
        }
        scaled_char_freq = {
            word: freq
            for word, freq in zip(
                char_freq, minmax_scale([c for c in char_freq.values()])
            )
        }

        with open(wordbank_path, "w", encoding="utf-8") as f:
            json.dump(
                [
                    {
                        "word": word,
                        "word_freq": freq,
                        "char_freq": scaled_char_freq[word],
                    }
                    for word, freq in scaled_word_freq.items()
                ],
                f,
                indent=4,
                sort_keys=True,
            )

    def word_guess(self, word: str, tiles: str) -> None:

        guess = [
            self.Letter(pos, char, color)
            for pos, (char, color) in enumerate(zip(word, tiles))
        ]

        removed_words = []
        for i, bank_word in enumerate([w.word for w in self.wordbank]):
            char_counter = Counter(bank_word)
            for g in [l for l in guess if l.color == "g"]:
                if not bank_word[g.pos] == g.char:
                    removed_words.append(i)
                    break
                # handles duplicate letter g + y/b case
                char_counter[g.char] -= 1
            else:
                for y in [l for l in guess if l.color == "y"]:
                    if not (bank_word[y.pos] != y.char and y.char in bank_word):
                        removed_words.append(i)
                        break
                    # handles duplicate letter y + b case
                    char_counter[y.char] -= 1
                else:
                    for b in [l for l in guess if l.color == "b"]:
                        if char_counter.get(b.char):
                            removed_words.append(i)
                            break

        # filter words
        self.wordbank = [
            w for i, w in enumerate(self.wordbank) if i not in removed_words
        ]
        self.guesses -= 1
        self.make_suggestion()

    def make_suggestion(self) -> None:

        suggestions = [
            self.Suggestion(
                w.word,
                # don't count word_freq for first guess
                (w.word_freq if self.guesses < 6 else 1)
                # don't count char_freq for last 3 guesses
                * (w.char_freq if self.guesses > 3 else 1),
            )
            for w in self.wordbank
        ]
        suggestions.sort(key=attrgetter("weight"), reverse=True)
        top_5 = [f"{s.word} ({s.weight:.4f})" for s in suggestions[:5]]

        len_found = len(self.wordbank)
        print(f"{self.max_words - len_found} words eliminated, {len_found} remaining")
        print(f"suggestions: {', '.join(top_5)}")
        print(f"{self.guesses} guesses remaining")

    def start(self) -> None:

        while self.guesses:

            while True:
                try:
                    word = input("enter guess (blank to quit): ").lower()
                    if not len(word):
                        return
                    if len(word) != 5 or not word.isalpha():
                        raise ValueError
                    break
                except ValueError:
                    print("guess must be 5 letters")

            while True:
                try:
                    tiles = input(
                        "enter tile colors (g)reen, (y)ellow, (b)lack: "
                    ).lower()
                    if not len(tiles):
                        return
                    if len(tiles) != 5 or not set("gyb").issuperset(tiles):
                        raise ValueError
                    break
                except ValueError:
                    print('tile colors must be 5 of "g", "y", or "b"')

            self.word_guess(word, tiles)


def main():

    wordlebot = WordleBot()
    wordlebot.start()


if __name__ == "__main__":
    main()
