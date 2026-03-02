"""
cli.py
Created on 2/17/26

Copyright (C) 2026 Mehmet Bertan Tarakcioglu

This file is part of OTP Dictionary Breaker.

OTP Dictionary Breaker is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

OTP Dictionary Breaker is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with OTP Dictionary Breaker.
If not, see <https://www.gnu.org/licenses/>.
"""
import argparse
from importlib.metadata import PackageNotFoundError, version
import os
from otp_dict_breaker.breaker import OTPDictBreaker
from otp_dict_breaker.tui import OTPDictBreakerTUI

cli_duck = """\
\033[1;93m\
    __
___( o)>
\\ <_. )
 `---´
\033[0m\
"""

epilogue_text = ("\n" + cli_duck + "\n" +
                "\033[93mThank you for using OTP Dictionary Breaker! Have a nice day :)\033[0m\n\n" +
                "\033[3;90mCopyright (c) 2026 Mehmet Bertan Tarakcioglu. Licensed under the AGPLv3 License.\033[0m")

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=
        "OTP Dictionary Breaker\n" +
        "  A CLI/TUI app and Python module that exploits the Many-Time Pad vulnerability where a single One-Time-Pad key is used for encrypting multiple ciphertexts.\n" +
        "  Using a frequency-ordered English word list to enhance automated crib-dragging, it recovers plaintext and key bytes with higher accuracy.\n" +
        "  The TUI makes it easy to incorporate manual guesses, guiding the dictionary attack further when necessary."
    )

    parser.add_argument(
        "ciphertext_dir",
        nargs="?",
        default=os.getenv("OTP_CTXT_DIR_PATH", "./"),
        help="Directory only containing ciphertext files in hex string format with any extension. Once decrypted, should resolve to ASCII bytes." +
             "Uses the current working directory if unspecified."
    )

    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Show the version number and exit."
    )
    
    parser.add_argument(
        "-p", "--print-only",
        action="store_true",
        help="For relatively simple ciphertexts, you may chose to skip the TUI manual character entry and print the results right away with this flag."
    )

    parser.add_argument(
        "-w", "--common-words",
        default=os.getenv("COMMON_WORDS_PATH", None),
        help=(
                "The path to a custom common words file. This should be a newline seperated, ordered list of most frequently used words in English. " +
                "Not case-sensitive. If unspecified, it uses a built-in list - highly recommended.")
    )
    
    parser.add_argument(
        "--no-numbers",
        action="store_true",
        help="If you know that your plaintext will not contain any digits [0-9], using this flag can increase accuracy."
    )
    
    parser.add_argument(
        "--no-punctuation",
        action="store_true",
        help="If you know that your plaintext will not contain any punctuation [, . \" ! ? : ; - # \" ( )], using this flag can increase accuracy."
    )

    parser.add_argument(
        "--allow-single-letters",
        action="store_true",
        help="By default, all single-letter words except for `a` and `i` are removed from the common-words dataset. " +
             "Use this flag to disable this behavior. Note that this is really helpful for web-based datasets and disabling can compromise accuracy.")
    
    parser.add_argument(
        "--candidates",
        type=int,
        default=2,
        help=
            "For each word with unknown spaces, the algorithm comes up with a list of dictionary words that will best fit." +
            "By default, we try 2 of the best candidates and give up if they both don't fit. You can set this to any number between 1-10, inclusive." +
            "2-3 seems to work the best for accuracy, but feel free to experiment!"
    )

    parser.add_argument(
        "-i", "--iterations",
        type=int,
        default=100,
        help="Maximum iterations for dictionary attack in cases where the ciphertext causes an infinite loop. Default: 100"
    )
    
    args = parser.parse_args()

    # Print version and exit if that's what the user wanted
    if args.version:
        try:
            human_readable_version__ = version("otp_dict_breaker")
        except PackageNotFoundError:
            human_readable_version__ = "undefined-dev"

        print(f"OTP Dictionary Breaker v{human_readable_version__}")
        print(epilogue_text)
        return 0

    common_words_list = None
    ciphertexts = []

    # Initialize the list of most common words from the file input if one was given
    # File should be split by newlines and ordered by word popularity.
    if args.common_words is not None:
        common_words_list = []
        try:
            with open(args.common_words, 'r') as words_file:
                for line in words_file:
                    common_words_list.append(line.rstrip().lower())
        except FileNotFoundError as e:
            print(f"\033[1;91mError: Cannot open customized common words file: \"{e.filename}\". Please make sure the path is correct.\033[0m")
            return 1

    # Read all ciphertext from the given directory
    try:
        for ctxt_filename in sorted(os.listdir(args.ciphertext_dir)):
            if ctxt_filename.startswith("."): continue

            if (args.common_words is not None) and (os.path.samefile(ctxt_filename, args.common_words)):
                print(f"\033[1;91mError: It seems like one of your ciphertext files is the same as the common words file. This seems unintentional.\033[0m")
                return 1

            try:
                with open(os.path.join(args.ciphertext_dir, ctxt_filename), "r") as ctxt_file:
                    ciphertexts.append(ctxt_file.read().replace('\n', ''))
            except IsADirectoryError as e:
                print(f"\033[1;93mWarning: Unexpectedly found a directory: \"{e.filename}\" among ciphertexts. Skipping...\033[0m")
                continue

    except (FileNotFoundError, PermissionError) as e:
        print(f"\033[1;91mError: Could not open file or directory: \"{e.filename}\". Please try one more time :)\033[0m")
        return 1

    # Create OTPDictBreaker object
    try:
        breaker = OTPDictBreaker(
            common_words_list=common_words_list,
            ciphertexts=ciphertexts,
            plaintext_has_numbers=not args.no_numbers,
            plaintext_has_punctuation=not args.no_punctuation,
            remove_single_letters_from_common_words=not args.allow_single_letters,
            number_top_candidates_to_try=args.candidates,
            max_decipher_iters=args.iterations
        )
    except ValueError as e:
        print(f"\033[1;91m{e}\033[0m")
        return 1
    except Exception as e:
        print(f"\033[1;91mError: Could not initialize OTPDictBreaker: {e}. ",
               "This is most likely an internal bug with the OTP Dictionary Breaker. Please consider reporting it :)\033[0m")
        raise
    
    if args.print_only:
        breaker.try_decipher(print_results=False)
    else:
        ui = OTPDictBreakerTUI(breaker)
        ui.run()
    
    print("\n\033[1m\033[95m------ Plaintexts (Hopefully) ------\033[0m\n")
    for i, plaintext in enumerate(breaker.maybe_plaintexts):
        print(f"\033[1;36m[{i}]\033[0m {plaintext}\n")

    print(f"\n\033[1m\033[95m------ OTP Key Recovered in Hex ({len(breaker.maybe_key)} bytes) ------\033[0m\n")
    key_hex = ''.join(
        f'\033[92m{format(b, "02x")}\033[0m' if b is not None else '\033[91m??\033[0m'
        for b in breaker.maybe_key
    )
    print(key_hex)

    if any(len(ctxt) > len(breaker.maybe_key) for ctxt in breaker.ciphertexts):
        print("\n\033[96m\033[1mP.S.\033[0m\033[96m Since this attack requires all ciphertexts (and the key) to be the same length, the messages have been truncated to the length of the shortest message. You should try and guess the rest later!\033[0m")

    print(epilogue_text)

    return None

if __name__ == "__main__":
    main()