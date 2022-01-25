#!/usr/bin/env python3

import logging
import re
from typing import Dict, List, Mapping, Set, Union

from .letterfrequency import letterfrequency


class Wordle:
    def __init__(
        self,
        word_list_file: str = "/usr/share/dict/words",
        word_length: int = 5,
        hard_mode: bool = True,
        relax_repeats: bool = False,
        answer: str = "",
        guesses: int = 6,
        initial_guess: str = "",
        top: int = 5,
        word_frequency_file: str = "",
        debug: bool = False,
    ):
        self.log = logging.getLogger(__name__)
        level = logging.INFO
        if debug:
            level = logging.DEBUG
        logging.basicConfig(level=level)
        self.answer = answer
        self.max_guesses = guesses
        self.top = top
        self.hard_mode = hard_mode
        assert hard_mode  # Haven't yet implemented non-hard-mode
        self.relax_repeats = relax_repeats
        self.exclude_letters: Set[str] = set()
        self.include_letters: Set[str] = set()
        self.word_length: int = word_length
        self.current_guess = initial_guess
        self.re_list: List[str] = ["^"]
        for i in range(word_length):
            self.re_list.append(".")
        self.re_list.append("$")
        self.load_wordlist(word_list_file)
        self.word_frequency: Dict[str, int] = {}
        self.match_pattern = "....."
        if not self.current_guess:
            # Pick the most-common-letters-word from the wordlist
            self.current_guess = self.get_best_guesses()[0]
            self.log.info(f"Best initial guess: {self.current_guess}")
        if word_frequency_file:
            # Do this after you pick the initial guess; picking the most
            # common word would be silly.  If you load a word frequency
            # file at all, this solver assumes you mean to solve with
            # word frequency rather than letter frequency.
            self.load_wordfreq(word_frequency_file)
        self.log.debug(
            f"Initialized: wordlist {word_list_file}, "
            + f"word count {len(self.wordlist)}, "
            + f"word length {word_length}."
        )

    def main_loop(self) -> None:
        for i in range(self.max_guesses):
            if not self.current_guess:
                self.enter_guess()
            self.log.info(f"Guessing try #{i + 1}: '{self.current_guess}'")
            if not self.answer:
                self.enter_response()
            else:
                self.calculate_response()
            if self.match_pattern == "!" * self.word_length:
                # That's it
                self.log.info(
                    f"Answer found: '{self.current_guess}' on try "
                    + f"{i + 1}."
                )
                return
            self.remove_guess()
            self.update_patterns()
            self.apply_patterns()
            self.log.debug(f"Remaining word count: {len(self.wordlist)}")
            best_guesses = self.get_best_guesses()
            if self.answer:
                self.current_guess = best_guesses[0]
            else:
                self.current_guess = ""
        raise ValueError("Maximum #guesses ({self.max_guesses}) exceeded!")

    def load_wordlist(self, filename: str) -> None:
        # /usr/share/dict/words is pretty canonical.  /usr/dict/words on
        # older Unixes.
        #
        # The actual Wordle wordlist can be found at:
        # https://gist.github.com/cfreshman/a03ef2cba789d8cf00c08f767e0fad7b
        #
        # Words you're allowed to guess in Wordle are at:
        # https://gist.github.com/cfreshman/cdcdf777450c5b5301e439061d29694c
        with open(filename) as f:
            wl = f.read().split()
        wl = [x.lower() for x in wl]
        wl = list(set(wl))  # Deduplicate
        wl = [x for x in wl if len(x) == self.word_length]
        self.wordlist = wl

    def load_wordfreq(self, filename: str) -> None:
        # I am using Peter Norvig's "count_1w.txt" from
        # http://norvig.com/ngrams/count_1w.txt
        # The format's pretty simple: lower-cased-word <whitespace> count
        # That file is MIT licensed.
        #
        # If you use something else, put it in that form.
        #
        # If you're doing this a lot, you probably want to create pre-filtered
        #  frequency files to match your wordlists, so you don't have to
        #  scan 1/3 of a million words each time you run.
        freq: Dict[str, int] = {}
        self.log.debug(f"Loading word frequency file {filename}")
        l_num = 0
        with open(filename) as f:
            for line in f:
                l_num += 1
                fields = line.strip().split()
                word, count = fields[0], int(fields[1])
                if len(word) != self.word_length:
                    continue
                if word not in self.wordlist:
                    continue
                freq[word] = count
        self.word_frequency = freq
        self.log.debug(f"Considered {l_num} words, kept {len(freq)}.")

    def enter_guess(self, guess: str = "") -> None:
        if guess:
            self.current_guess = guess
            return
        while True:
            guess = input("Guess word > ")
            guess = guess.lower()
            if len(guess) == self.word_length:
                if guess in self.wordlist:
                    break
            print(f"{guess} is not in the currently-allowed list.")
        self.current_guess = guess

    def enter_response(self, response: str = "") -> None:
        if response:
            self.match_pattern = response
            return  # for testing
        while True:
            response = input(
                "Enter response: . = 'no', ! = 'correct', "
                + "? = 'in word, wrong position' > "
            )
            if len(response) != self.word_length:
                continue
            s_r = set(response)
            okset = set([".", "!", "?"])
            if s_r <= okset:
                self.match_pattern = response
                break

    def calculate_response(self) -> None:
        resp = ""
        for idx, c in enumerate(self.current_guess):
            if c == self.answer[idx]:
                resp = f"{resp}!"
                continue
            if c in self.answer:
                resp = f"{resp}?"
                continue
            resp = f"{resp}."
        self.log.debug(f"Response is {resp}")
        self.match_pattern = resp

    def remove_guess(self) -> None:
        self.wordlist.remove(self.current_guess)

    def update_patterns(self) -> None:
        self.log.debug(f"current_guess: {self.current_guess}")
        pattern = self.match_pattern
        for idx, ch in enumerate(pattern):
            c = self.current_guess[idx]
            p_i = idx + 1
            current_set = self.re_list[p_i]
            if not current_set.startswith("[^") and current_set != ".":
                # We know what letter it is.  Keep going.
                continue
            if ch == "!":
                # This is correct
                self.re_list[p_i] = c
                # And since we have an exact match, we can drop it from
                #  include_letters
                self.include_letters.discard(c)
            elif ch == "?":
                # This letter is in the word, but not in that place
                if current_set == ".":
                    current_set = f"[^{c}]"
                else:
                    setlets = str(current_set)[2:-1]
                    current_lets = set(setlets)
                    current_set = str(current_lets | {c})
                    current_set = f"[^{''.join(current_set)}]"
                self.re_list[p_i] = current_set
                if c not in self.re_list:
                    self.include_letters = self.include_letters | {c}
            elif ch == ".":
                self.exclude_letters = self.exclude_letters | {c}
            else:
                raise ValueError(f"Response character {ch} not in '.?!'")
        self.log.debug(f"include: {self.include_letters}")
        self.log.debug(f"exclude: {self.exclude_letters}")

    def apply_patterns(self) -> None:
        # First get rid of anything that doesn't have all of the letters we
        #  know we need, or has any letters we know we don't want.
        self.log.debug(
            f"before applying patterns: {len(self.wordlist)} "
            + "words remain."
        )
        filtered = []
        for w in self.wordlist:
            wset = set(w)
            if self.exclude_letters:
                overlap = self.exclude_letters & wset
                if len(overlap) > 0:
                    continue
            if self.include_letters:
                if self.include_letters <= wset:
                    filtered.append(w)
                    continue
            else:
                filtered.append(w)
        self.log.debug(f"After filtering: {len(filtered)} words remain.")
        updated = []
        re_str = "".join(self.re_list)
        regex = re.compile(re_str)
        self.log.debug(f"matching regex: {regex}")
        for w in filtered:
            if re.match(regex, w) is not None:
                updated.append(w)
        updated = list(set(updated))
        self.log.debug(
            f"After regex application: {len(updated)} " + "words remain."
        )
        self.wordlist = updated

    def get_best_guesses(self) -> List[str]:
        if self.word_frequency:
            freqs = self.get_word_frequencies()
            guesses = self.apply_frequency_metric(freqs)
        else:
            weights = self.get_character_weights()
            weighted_guesses = self.sort_by_weight(weights)
            guesses = self.limit_repeats(weighted_guesses)
        if len(guesses) < 1:
            raise ValueError("Out of possible words!")
        best_guess = guesses[: self.top]
        g_str = "guess"
        if self.top > 1:
            g_str = "guesses"
        g_log = f"Current best {g_str}: {', '.join(best_guess)}"
        if self.answer:
            self.log.debug(g_log)
        else:
            self.log.info(g_log)
        return best_guess

    def get_word_frequencies(self) -> Dict[str, int]:
        w_freq = {}
        for w in self.wordlist:
            w_freq[w] = self.word_frequency.get(w, 0)
        return w_freq

    def apply_frequency_metric(self, w_freq: Dict[str, int]) -> List[str]:
        #
        # There's some sort of theory that we shouldn't use very common
        #  words, because the puzzle word will be somewhat hard
        #
        # We can work that out later.  For right now we're just going to
        #  sort by frequency.
        return self.sort_by_weight(w_freq)

    def get_character_weights(self) -> Dict[str, float]:
        weights = {}
        for word in self.wordlist:
            weights[word] = sum([letterfrequency[c] for c in word])
        return weights

    def sort_by_weight(
        self, weights: Mapping[str, Union[int, float]]
    ) -> List[str]:
        return [
            x[0]
            for x in sorted(weights.items(), key=lambda y: y[1], reverse=True)
        ]

    def limit_repeats(self, guesses: List[str]) -> List[str]:
        # We prefer to repeat as few letters as possible, so we can eliminate
        # more at each stage.  This relies on sorted() being stable, but that
        # is indeed guaranteed.
        #
        # If self.relax_repeats is set, then if we have all but two
        #  letters identified, we just return our input.  This may be an
        #  optimization, although it's not clear whether it is a net
        #  benefit or not.
        if self.relax_repeats:
            right_ltrs = self.match_pattern.count("!")
            if (self.word_length - right_ltrs) < 3:
                return guesses
        diff_ltrs = {}
        for word in guesses:
            diff_ltrs[word] = len(set(word))
        return [
            x[0]
            for x in sorted(
                diff_ltrs.items(), key=lambda y: y[1], reverse=True
            )
        ]
