#!/usr/bin/env python3

import argparse

from .wordle import Wordle


def main() -> None:
    parser = argparse.ArgumentParser(description="Solve a Wordle puzzle")
    parser.add_argument("-a", "--answer", help="the correct word", default="")
    parser.add_argument(
        "-d", "--debug", help="debug", action="store_true", default=False
    )
    parser.add_argument(
        "-f",
        "--file",
        help="file of allowable words",
        default="/usr/share/dict/words",
    )
    parser.add_argument(
        "-g", "--guesses", help="number of guesses", default=6, type=int
    )
    parser.add_argument(
        "-i", "--initial-guess", help="initial guess", default=""
    )
    parser.add_argument(
        "-l", "--length", help="word length", type=int, default=5
    )
    parser.add_argument(
        "-r",
        "--relax-repeats",
        help="Relax letter maximization if only two remain",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-t",
        "--top",
        help="# of guesses to display (interactive)",
        type=int,
        default=5,
    )
    parser.add_argument(
        "-w",
        "--word-frequency-file",
        help="File containing words and their frequency",
    )
    args = parser.parse_args()
    w = Wordle(
        word_list_file=args.file,
        word_frequency_file=args.word_frequency_file,
        debug=args.debug,
        word_length=args.length,
        guesses=args.guesses,
        answer=args.answer,
        initial_guess=args.initial_guess,
        relax_repeats=args.relax_repeats,
        top=args.top,
    )
    w.main_loop()


if __name__ == "__main__":
    main()
