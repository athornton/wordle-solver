"""
Use this fragment with `python3 -i interactive.py`

Then you'd do something like

>>> w = WordleSolver(character_frequency_file=data['sf'],
                     word_list_file=data['5w'],
                     debug=True,
                     answer='hairy',
                     initial_guess='stone',
                     guesses=2
                    )

"""
from os.path import dirname, join, realpath

# Yes, we aren't actually generating the object in this fragment, and the data
#  dict really does come from our test fixture.
# pylint: disable=unused-import
from wordle_solver.wordle_solver import WordleSolver  # noqa: F401

datadir = realpath(join(dirname(__file__), "../tests/static"))
data = {
    "5w": join(datadir, "5x1000.txt"),
    "6w": join(datadir, "6x800.txt"),
    "5f": join(datadir, "5x1000.freq"),
    "6f": join(datadir, "6x800.freq"),
    "ff": join(datadir, "flat.freq"),
    "sf": join(datadir, "standard.freq"),
    "mm": join(datadir, "mastermind.txt"),
    "pm": join(datadir, "primel.txt"),
}  # pylint: disable=duplicate-code
# The duplicate code warning is actually disabled in pyproject.toml, because
# ignoring it with a comment doesn't work:
# https://github.com/PyCQA/pylint/issues/214
