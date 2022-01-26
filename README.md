# Wordle Solver

It does what it says on the tin.

This solver currently plays only on hard mode.

## Interactive use

If you're using it interactively--that is, without specifying the
`--answer` option, input the results you get as a five-character string,
where `.` means it's not in the word, `?` means it's in the word but in
the wrong place, and `!` means it's in the right place.  In the Wordle
UI, `!` is green, and `?` is yellow.

## Non-interactive

If you know the answer and want to see if this program will solve it
faster than you did, try `--answer` and see how many guesses it takes.

## Word frequency

If you feed it a word-frequency file, the solver will assume you mean to
solve on the basis of word frequency rather than character frequency.
(Character frequency is the default.)

## Options

The input word list can be set with `--file`.  If you don't set it, you
get `/usr/share/dict/words`.  If you want to use a word-frequency file, use
the `--word-frequency-file` option to set it.

You can set the initial guess with `--initial-guess`.  From a
character-frequency standpoint, at least with the dictionaries I've been
using, `atone` is the best starting guess.  I usually like to start with
`arise` when I'm actually playing.

If you use `--relax-repeats` then the solver will no longer prefer
unrepeated characters when there are only two unknowns.  This might or
might not be an optimization.

If you set `--top` you will get more or fewer displayed best guesses
than the default of 5.

You can let it run for more guesses with `--guesses` (the default is 6)
and you can play with different word lengths with `--length` (the
default is 5).

`--debug` will emit copious output about what the solver is doing as it
does it.

## Developing

If you want to play around with this yourself, ``make init`` will set up
the pre-commit hooks for you.  The solver itself has no external
requirements: everything in it is in the Python 3.8 standard library;
however, the test suite and pre-commit hooks have some requirements.
