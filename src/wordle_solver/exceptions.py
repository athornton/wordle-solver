"""
WordleSolver-specific exceptions
"""


class AnswerFound(Exception):
    """
    We know the answer.  It's an exception because we want to use it to
    jump out of several nested loops.
    """


class OutOfGuesses(Exception):
    """
    We failed to guess the answer in the number of guesses allowed.
    """
