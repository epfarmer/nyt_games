import json
import os
from collections import Counter, defaultdict, namedtuple
from operator import attrgetter
from pathlib import Path

from nltk.corpus import words
from sklearn.preprocessing import minmax_scale
from wordfreq import zipf_frequency


class WordleBot:
    def __init__(self, auto: bool = False):

        self.auto = auto

        self.wordbank_file = Path(os.path.dirname(__file__)) / "wordle_bank.json"

        self.Word = namedtuple("Word", ["word", "word_freq", "char_freq"])
        self.Tile = namedtuple("Tile", ["pos", "char"])
        self.Suggestion = namedtuple("Suggestion", ["word", "weight"])

        self.load_wordbank()
        self.guesses = 6
        self.start()

    def load_wordbank(self) -> None:

        if not self.wordbank_file.is_file():
            self.generate_wordbank()

        with open(self.wordbank_file) as f:
            self.wordbank = [
                self.Word(w["word"], w["word_freq"], w["char_freq"])
                for w in json.load(f)
            ]
            self.max_words = len(self.wordbank)

    def generate_wordbank(self) -> None:

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

        with open(self.wordbank_file, "w", encoding="utf-8") as f:
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

    def word_guess(self, word: str, tile_colors: str) -> None:

        guess = defaultdict(list)
        for pos, (char, color) in enumerate(zip(word, tile_colors)):
            guess[color].append(self.Tile(pos, char))

        # filter words
        self.wordbank = [w for w in self.wordbank if self.word_check(w.word, guess)]
        self.guesses -= 1
        print(
            f"{self.max_words - (len_found := len(self.wordbank))} words eliminated, {len_found} remaining"
        )

    def word_check(self, word: str, guess: dict[str, list[tuple]]) -> bool:
        char_counter = Counter(word)

        for g in guess["g"]:
            if word[g.pos] != g.char:
                return False
            # handles duplicate letter g + y/b case
            char_counter[g.char] -= 1

        for y in guess["y"]:
            if word[y.pos] == y.char or not char_counter.get(y.char):
                return False
            # handles duplicate letter y + b case
            char_counter[y.char] -= 1

        for b in guess["b"]:
            if char_counter.get(b.char):
                return False

        return True

    def make_suggestion(self) -> str:

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

        if not len(suggestions):
            raise IndexError

        suggestions.sort(key=attrgetter("weight"), reverse=True)

        if not self.auto:
            print(f"suggestions: {', '.join([s.word for s in suggestions[:5]])}")

        return suggestions[0].word

    def start(self) -> None:
        word = self.make_suggestion()
        while self.guesses:

            if not self.auto:
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
            else:
                print(f"autosuggest: {word}")

            while True:
                try:
                    tile_colors = input(
                        "enter tile colors (g)reen, (y)ellow, (b)lack: "
                    ).lower()
                    if not len(tile_colors):
                        return
                    if len(tile_colors) != 5 or not set("gyb").issuperset(tile_colors):
                        raise ValueError
                    break
                except ValueError:
                    print('tile colors must be 5 of "g", "y", or "b"')

            self.word_guess(word, tile_colors)
            try:
                word = self.make_suggestion()
            except IndexError:
                print("No matching words found")
                return
            print(f"{self.guesses} guesses remaining\n")


def main():
    WordleBot(auto=False)


if __name__ == "__main__":
    main()
