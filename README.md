# Wordle Solver

It does what it says on the tin.

If, somehow, you have no idea what Wordle is, yet you're here:
https://www.powerlanguage.co.uk/wordle/

Basically, it's "Mastermind" with a really nice UI.

This solver currently plays only on hard mode.  If you don't follow
Wordle nomenclature, that means: when you have a letter identified but
in the wrong position, you have to use that letter in your next guess.
If you have a letter in the right position, it's locked in for the rest
of your guesses.

## Interactive use

If you're using it interactively--that is, without specifying the
`--answer` option, input the results you get as a five-character string,
where `.` means it's not in the word, `?` means it's in the word but in
the wrong place, and `!` means it's in the right place.  In the Wordle
UI, `!` is green, and `?` is yellow.

So: if you are being a horrible person and using this to cheat at
Wordle, what you do is put your initial guess into both this program and
Wordle.  Then you take Wordle's answer, transcribe it into a result this
program will accept (that is, a five-character string consisting of only
`!`, `?`, and `.`), put that into the program, and then type the next
suggestion it gives you into Wordle.

If you end up in the trap of words ending in "atch" we can't really help
you.  There are seven pretty common five-letter words like that, and you
have only six guesses in Wordle.

## Non-interactive

If you know the answer and want to see if this program will solve it
faster than you did, try `--answer` and see how many guesses it takes.
You may want to try this with a word frequency file, or by relaxing
constraints on repeated letters, to see how much (if any) better it
does.

## Word frequency

If you feed it a word-frequency file, the solver will assume you mean to
solve on the basis of word frequency rather than character frequency.
(Character frequency is the default.)

## Options

The input word list can be set with `--file`.  If you don't set it, you
get `/usr/share/dict/words`.

If you want to use a different word-frequency file, use
the `--word-frequency-file` option to set it.

If you do not specify a character-frequency file, the solver will use
the observed letter frequency from your word list file.  If you have a
very large dictionary or a very slow computer, this might take a while
to generate.  If you want to specify a character frequency file, use
`--character-frequency-file`.

You can set the initial guess with `--initial-guess`.  From a
character-frequency standpoint, at least with the dictionaries I've been
using, `atone` is the best starting guess.  I usually like to start with
`arise` when I'm actually playing.

If you use `--relax-repeats` then the solver will no longer prefer
unrepeated characters when there are only two unknowns.  This might or
might not be an optimization.

If you set `--top` you will get more or fewer displayed best guesses
than the default of 5.

You can let it run for more guesses with `--guesses` (the default is 6,
per Wordle) and you can play with different word lengths with `--length`
(the default is 5, again just like Wordle).

`--debug` will emit copious output about what the solver is doing as it
does it.

## Generating word and character frequency files

The program [`generate_test_data`](scripts/generate_test_data) will
create word frequency files for the most common 1000 five-letter words
and the most common 800 six-letter words, as well as character frequency
in English text, and dictionary lists for playing
[Primel](https://converged.yt/primel/) and
[Mastermind](https://en.wikipedia.org/wiki/Mastermind_(board_game)).

These files will be generated in the `tests/static` directory.  You can
also generate them with `make testdata` in the top-level directory.

## Playing other similar games

### Primel

The solver also works fine for Primel, although you will need to give it
an input word list of all five-digit primes (which `make testdata` will
generate for you).

### Mastermind

The solver can also play Mastermind.  Give it an input word list of all
four-character combinations of the digits `1` through `6` (`make testdata`
will generate this as well), and set `--length` to `4`).

## Developing

If you want to play around with this yourself, ``make init`` will set up
the pre-commit hooks for you.  The solver itself has no external
requirements: everything in it is in the Python 3.8 standard library;
however, the test suite and pre-commit hooks have some external packages
they require.

There is also a
[Python fragment for interactive use](scripts/interactive.py) that can
be used to create a `WordleSolver` object and examine its internal state
as play proceeds.  Basic instructions for use are in the file.
