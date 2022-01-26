"""
Unit tests for the Wordle solver.
"""
import logging
from typing import Dict

import pytest

from wordle_solver.exceptions import OutOfGuesses
from wordle_solver.wordle_solver import WordleSolver


def test_minimal_wordle_class(data: Dict[str, str]) -> None:
    """
    Create a minimal WordleSolver and verify its attributes.
    """
    w = WordleSolver(word_list_file=data["5w"])
    assert w.word_length == 5
    assert w.top == 5
    assert w.max_guesses == 6
    assert w.relax_repeats is False
    assert w.log.level == logging.INFO
    assert len(w.wordlist) == 1000
    assert w.include_letters == set()
    assert w.exclude_letters == set()
    assert "".join(w.re_list) == "^.....$"
    assert w.attempt == 1
    assert w.match_pattern == "....."
    assert w.answer == ""
    assert len(w.word_frequency) == 0


def test_wordle_class_parameters(data: Dict[str, str]) -> None:
    """
    Create a WordleSolver with non-default attributes and verify those.
    """
    w = WordleSolver(
        word_list_file=data["6w"],
        word_frequency_file=data["6f"],
        word_length=6,
        relax_repeats=True,
        answer="create",
        initial_guess="offers",
        top=3,
        guesses=4,
        debug=True,
    )
    assert w.word_length == 6
    assert w.top == 3
    assert w.max_guesses == 4
    assert w.relax_repeats is True
    assert w.log.level == logging.DEBUG
    assert len(w.wordlist) == 800
    assert w.current_guess == "offers"
    assert "".join(w.re_list) == "^......$"
    assert w.match_pattern == "......"
    assert w.answer == "create"
    assert len(w.word_frequency) == 800


def test_success(data: Dict[str, str]) -> None:
    """
    Ensure the happy path works.
    """
    w = WordleSolver(
        word_list_file=data["5w"],
        word_frequency_file=data["5f"],
        answer="happy",
    )
    w.main_loop()
    assert w.current_guess == w.answer


@pytest.mark.xfail(raises=OutOfGuesses)
def test_failure(data: Dict[str, str]) -> None:
    """
    Ensure we fail as expected if we run out of guesses.
    """
    w = WordleSolver(word_list_file=data["5w"], answer="watch", guesses=3)
    w.main_loop()


@pytest.mark.xfail(raises=NotImplementedError)
def test_not_hard_mode(data: Dict[str, str]) -> None:
    """
    Check that we fail (for now) if we try to turn hard mode off.
    """
    w = WordleSolver(
        word_list_file=data["5w"], answer="error", hard_mode=False
    )
    w.main_loop()


def test_relax_repeats(data: Dict[str, str]) -> None:
    """
    Verify that we get different answers if we turn off repeated-letter
    rejection or a known word list.
    """
    w = WordleSolver(
        word_list_file=data["5w"], answer="sissy", initial_guess="atone"
    )
    w.wordlist = ["atone", "kissy", "missy", "sissy"]
    initial_length = len(w.wordlist)
    w.main_loop()
    first = w.attempt
    assert first == initial_length  # Because all candidates already have
    # 's' in them, the solver will choose 'sissy' last of all.
    w = WordleSolver(
        word_list_file=data["5w"],
        answer="sissy",
        initial_guess="atone",
        relax_repeats=True,
    )
    w.wordlist = ["atone", "kissy", "missy", "sissy"]
    w.main_loop()
    assert w.attempt < first  # But 's' is more common than 'm' and 'k',
    # so this time it will have been chosen sooner.


def test_word_freq(data: Dict[str, str]) -> None:
    """
    Verify that word and letter frequency behave differently.
    """
    # First, we do letter frequency.
    w = WordleSolver(
        word_list_file=data["6w"],
        answer="answer",
        word_length=6,
        initial_guess="button",
    )
    char_frequency_guess = w.current_guess  # 'linear', as it happens
    w.loop_once()
    w = WordleSolver(
        word_list_file=data["6w"],
        word_frequency_file=data["6f"],
        answer="answer",
        word_length=6,
        initial_guess="button",
    )
    w.loop_once()
    assert char_frequency_guess != w.current_guess  # 'change'


def test_internal_state(data: Dict[str, str]) -> None:
    """
    Make sure that our internal data structures behave as expected.
    Specifically, we're testing:
    a) winnowing down of word lists,
    b) our include and exclude sets, and
    c) the matching regular expression we are constructing.
    """
    w = WordleSolver(
        word_list_file=data["6w"],
        answer="answer",
        word_length=6,
        initial_guess="button",
    )
    w.loop_once()
    w.attempt += 1
    assert len(w.wordlist) == 78
    w.loop_once()
    w.attempt += 1
    assert len(w.wordlist) == 1  # Yep, it really goes get it on the third try.
    assert w.include_letters == set(["a", "e", "n"])
    assert w.exclude_letters == set(["b", "u", "t", "o", "i", "l"])
    assert "".join(w.re_list) == "^..[^n][^e][^a]r$"
