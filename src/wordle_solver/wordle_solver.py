"""
This is the main class for a Wordle solver.
"""

import logging
import re
from typing import Dict, List, Mapping, Set, Union

from .exceptions import AnswerFound, OutOfGuesses


class WordleSolver:
    """
    Solve a Wordle-style puzzle.  Word length and whether to use word
    frequency or just letter frequency are options, as are how many
    guesses are allowed.
    """

    # Yes, the WordleSolver has a lot of attributes, and yes, I like using
    #  short variable names in my methods.  And I really don't care if I burn
    #  a few hundred microseconds interpolating a string I'm not going to
    #  emit.

    # pylint: disable="too-many-instance-attributes"
    # pylint: disable="invalid-name"
    # pylint: disable="logging-not-lazy"
    # pylint: disable="logging-fstring-interpolation"

    def __init__(
        self,
        word_list_file: str = "/usr/share/dict/words",
        word_length: int = 5,
        easy_mode: bool = False,
        relax_repeats: bool = False,
        answer: str = "",
        guesses: int = 6,
        initial_guess: str = "",
        top: int = 5,
        word_frequency_file: str = "",
        character_frequency_file: str = "",
        debug: bool = False,
    ):  # pylint: disable="too-many-arguments"
        self.log = logging.getLogger(__name__)
        level = logging.INFO
        if debug:
            level = logging.DEBUG
        logging.basicConfig(level=level)
        self.log.setLevel(level)
        self.answer = answer
        self.max_guesses = guesses
        self.top = top
        self.easy_mode = easy_mode
        if easy_mode:
            raise NotImplementedError("Easy mode not yet implemented")
        self.relax_repeats = relax_repeats
        self.exclude_letters: Set[str] = set()
        self.include_letters: Set[str] = set()
        self.word_length: int = word_length
        self.current_guess = initial_guess
        self.re_list: List[str] = ["^"]
        for _ in range(word_length):
            self.re_list.append(".")
        self.re_list.append("$")
        self.wordlist: List[str] = []
        self.character_frequency: Mapping[str, Union[int, float]] = {}
        self.word_frequency: Mapping[str, Union[int, float]] = {}
        self.load_wordlist(word_list_file)
        self.attempt: int = 1
        self.match_pattern = "." * self.word_length
        # By default, you will generate character frequencies from your
        # input word list.  This will cause a noticeable delay in startup if
        # you're using a full-size dictionary.
        #
        # Thus, you might want to specify a character frequency file.
        #
        # You can generate a character frequency file that's pretty accurate
        # for English text by running 'make testdata' from the top of the
        # repository.  It will then be in tests/static/standard.freq .
        if character_frequency_file:
            self.character_frequency = self.load_frequency_file(
                character_frequency_file, char=True
            )
        else:
            self.character_frequency = self.generate_frequencies()
        # In any event, you're going to need character frequency here.
        if not self.current_guess:
            # Pick the most-common-letters-word from the wordlist
            self.current_guess = self.get_best_guesses()[0]
            self.log.info(f"Best initial guess: '{self.current_guess}'")
        if word_frequency_file:
            # Do this after you pick the initial guess; picking the most
            # common word would be silly.  If you load a word frequency
            # file at all, this solver assumes you mean to solve with
            # word frequency rather than letter frequency.
            self.word_frequency = self.load_frequency_file(word_frequency_file)
        self.log.debug(
            f"Initialized: wordlist {word_list_file}, "
            + f"word count {len(self.wordlist)}, "
            + f"word length {word_length}."
        )

    def load_wordlist(self, filename: str) -> None:
        """
        Ingest the word list.  Note that this is separate from the
        word_length parameter, because you may well want to use a standard
        dictionary and restrict by length without needing to produce the
        filtered directory as its own file.
        """
        # /usr/share/dict/words is pretty canonical.  /usr/dict/words on
        # older Unixes.
        #
        # The actual Wordle wordlist can be found at:
        # https://gist.github.com/cfreshman/a03ef2cba789d8cf00c08f767e0fad7b
        #
        # Words you're allowed to guess in Wordle are at:
        # https://gist.github.com/cfreshman/cdcdf777450c5b5301e439061d29694c
        with open(filename, encoding="utf-8") as f:
            wordlist = f.read().split()
        wordlist = [x.lower() for x in wordlist]
        wordlist = list(set(wordlist))  # Deduplicate
        wordlist = [x for x in wordlist if len(x) == self.word_length]
        self.wordlist = wordlist

    def load_frequency_file(
        self, filename: str, char: bool = False
    ) -> Mapping[str, Union[int, float]]:
        """
        Just like load_wordlist, but it expects each word to have whitespace
        after that and then a frequency count.

        If char is true, you're loading a character-frequency file, in which
        case, "word length" is 1 and we skip the check to see if that word
        is in the word list.
        """
        # I am using Peter Norvig's "count_1w.txt" from
        # http://norvig.com/ngrams/count_1w.txt
        # That file is MIT licensed.
        #
        # If you're doing this a lot, you probably want to create pre-filtered
        #  frequency files to match your wordlists, so you don't have to
        #  scan 1/3 of a million words each time you run.
        freq: Dict[str, int] = {}
        self.log.debug(f"Loading frequency file {filename}")
        l_num = 0
        word_length = self.word_length
        if char:
            word_length = 1
        with open(filename, encoding="utf-8") as f:
            for line in f:
                l_num += 1
                fields = line.strip().split()
                word, count = fields[0], int(fields[1])
                if len(word) != word_length:
                    continue
                if word not in self.wordlist and not char:
                    continue
                freq[word] = count
        if not char:
            self.log.debug(f"Considered {l_num} words, kept {len(freq)}.")
        return freq

    def generate_frequencies(self) -> Dict[str, int]:
        """
        Generate character frequency from the actual word list (which is
        already lowercased and deduplicated).
        """
        cf = {}
        for w in self.wordlist:
            for c in w:
                if c not in cf:
                    cf[c] = 1
                else:
                    cf[c] += 1
        # Sorting here is purely for the debugging output to look prettier
        #  and make it easier to see what the most common characters are.
        s_cf = self.sort_by_weight(cf)
        sorted_frequencies = {}
        for x in s_cf:
            sorted_frequencies[x] = cf[x]
        self.log.debug(f"Dynamic character frequencies: {sorted_frequencies}")
        return sorted_frequencies

    def main_loop(self) -> None:
        """
        This continues until it runs out of guesses or finds the answer.
        """
        while True:
            try:
                self.loop_once()
            except AnswerFound as answer:
                self.log.info(answer)
                return

    def loop_once(self) -> None:
        """
        This is the logic for acquiring, testing, and refining a single guess.
        """
        self.get_guess_and_response()
        self.test_if_complete()
        self.remove_guess()
        self.update_patterns()
        self.apply_patterns()
        self.log.debug(f"Remaining word count: {len(self.wordlist)}")
        best_guesses = self.get_best_guesses()
        if self.answer:
            self.current_guess = best_guesses[0]
        else:
            self.current_guess = ""

    def get_guess_and_response(self) -> None:
        """
        Get a guess and a response either interactively or noninteractively.
        """
        if not self.current_guess:
            self.enter_guess()
        self.log.info(f"Guessing try #{self.attempt}: '{self.current_guess}'")
        if not self.answer:
            self.enter_response()
        else:
            self.calculate_response()

    def test_if_complete(self) -> None:
        """
        Did we find the word?
        """
        if self.match_pattern == "!" * self.word_length:
            # That's it
            correct = (
                f"Answer found: '{self.current_guess}' "
                + f"on attempt {self.attempt}."
            )
            raise AnswerFound(correct)
        # That wasn't it.  Did we run out of guesses?
        self.attempt += 1
        if self.attempt >= self.max_guesses:
            raise OutOfGuesses(
                f"Maximum #guesses ({self.max_guesses}) " + "exceeded!"
            )

    def enter_guess(self, guess: str = "") -> None:
        """
        Get a guess interactively from the user.
        """
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

    def enter_response(self) -> None:
        """
        Solicit a response string interactively from the user.
        """
        response = ""
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
        """
        If we know the answer, calculate the response string.
        """
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
        """
        We now know *one* word that isn't the right answer.
        """
        self.wordlist.remove(self.current_guess)

    def update_patterns(self) -> None:
        """
        This builds the regular expression that matches possible correct
        answers, and updates the sets of letters we know are, and are not,
        in the answer.
        """
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
        """
        Filter the wordlist based on the information we now have.
        """
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
        """
        Now we have a reduced wordlist, so we need to choose the best guesses
        from it, for some metric of "best."

        If we have a word frequency file, we'll use that; otherwise we will
        use letter frequency.
        """
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

    def get_word_frequencies(self) -> Mapping[str, Union[int, float]]:
        """
        This simply builds a dictionary mapping each remaining word to its
        frequency.
        """
        w_freq = {}
        for w in self.wordlist:
            w_freq[w] = self.word_frequency.get(w, 0)
        return w_freq

    def apply_frequency_metric(
        self, w_freq: Mapping[str, Union[int, float]]
    ) -> List[str]:
        """
        This is (currently) a placeholder that just returns more frequent
        words first.

        In theory there's a set of metrics you could use to downweight
        extremely common words on the theory they're too easy.  In practice
        there just aren't all that many five-letter words that are
        generally recognized, and it doesn't seem that Wordle tries to pick
        particularly nasty ones, so...this may never be useful.
        """
        return self.sort_by_weight(w_freq)

    def get_character_weights(self) -> Dict[str, float]:
        """
        Just add the frequencies of each letter in the word.  This is
        pretty crude, because it doesn't do anything to determine common
        bigrams and trigrams, but in practice it seems to be pretty decent.

        It might also be superfluous.  The word list just isn't that large,
        for actual Wordle, anyway.
        """
        weights = {}
        for word in self.wordlist:
            weights[word] = sum([self.character_frequency[c] for c in word])
        return weights

    def sort_by_weight(
        self, weights: Mapping[str, Union[int, float]]
    ) -> List[str]:
        """
        Return the words with the highest weight (meaning, summed letter
        frequency, or word frequency) first.
        """
        # pylint: disable=no-self-use
        return [
            x[0]
            for x in sorted(weights.items(), key=lambda y: y[1], reverse=True)
        ]

    def limit_repeats(self, guesses: List[str]) -> List[str]:
        """
        We prefer to repeat as few letters as possible, so we can eliminate
        more at each stage.  This relies on sorted() being stable, but that
        is indeed guaranteed.

        If self.relax_repeats is set, then if we have all but two
        letters identified, we just return our input.  This may be an
        optimization, although it's not clear whether it is a net
        benefit or not.
        """
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
