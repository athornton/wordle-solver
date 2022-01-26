"""
Test fixtures for our unit tests.
"""
from os.path import dirname, join
from typing import Dict

import pytest

from wordle_solver.wordle_solver import WordleSolver


@pytest.fixture(scope="session")
def data() -> Dict[str, str]:
    """
    This just saves us some verbiage when setting up WordleSolvers.
    """
    datadir = join(dirname(__file__), "static")
    return {
        "5w": join(datadir, "5x1000.txt"),
        "6w": join(datadir, "6x800.txt"),
        "5f": join(datadir, "5x1000.freq"),
        "6f": join(datadir, "6x800.freq"),
        "ff": join(datadir, "flat.freq"),
    }


@pytest.fixture
def standard_solver(data) -> WordleSolver:  # pylint: disable=W0621
    """
    Return a solver with usual Wordle parameters
    """
    return WordleSolver(word_list_file=data["5w"])
