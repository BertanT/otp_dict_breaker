# OTP Dictionary Breaker
A CLI/TUI app and Python module that exploits the Many-Time Pad vulnerability where a single One-Time-Pad key is used for encrypting multiple ciphertexts.
Using a frequency-ordered English word list to enhance automated crib-dragging, it recovers plaintext and key bytes with higher accuracy. 
The TUI makes it easy to incorporate manual guesses, guiding the dictionary attack further when necessary.

## Usage
### Quick Start
Install and break ciphertexts in different text files within a directory.
```
pip3 install otp-dict-breaker
otp-dict-breaker /path/to/ciphertext/dir
```

Run `--help` or continue on reading for details :)

### Detailed Installation for Contributing and Experimentation
This project offers both a CLI/TUI front-end and a Python module that you can use to carry out this attack.
You can refer to the inline comments and Docstrings in the source files for the module. Below is a quick guide
to help you get started with the TUI.

Clone this repository to your machine and change your working directory.
You can also install from pip like above and skip this step, but the examples will not be included.

```
git clone https://github.com/BertanT/otp_dict_breaker.git
cd otp_dict_breaker
```

Install a local version of this package. It is best to do this in a [Virtual Environment](https://docs.python.org/3/tutorial/venv.html).
After you have activated your Virtual Environment, continue to install this package locally in *editable* mode. This is the recommended way
if you are installing this package for contributions, as the changes in the source code will reflect on the package without re-installing.
If you don't intend to modify this project's source code, simply remove the `-e` parameter.
```
pip3 install -e .
```

You are all set! Now for a quick little demo...
```
cd examples
otp-dict-breaker otp-ctxt
```

After running the otp-dict-breaker attack once, the TUI will launch to let you manually fill in the missing characters represented with
hash symbols (#). Use the keyboard shortcuts outlined at the bottom of your screen. 
As the algorithm can make mistakes, you can also overwrite existing letters.

At any point, you may choose to re-run the dictionary attack on the plaintexts you updated with 'ctrl+r'. As you manually guess some of the
characters, the algorithm can utilize this new data to make better guesses next time to save you some time.

When you are done, press `ctrl+c` to quit. The recovered key (so far) and the current state of the plaintexts will be reported.

For a much simpler example to break, run the following command.

You can use a positional argument to specify a directory containing ciphertext files. By default, it uses the current working directory. 

Use `-p` to avoid the TUI and manual entry when you don't need it.
```
otp-dict-breaker otp-ctxt-simple/ -p
```

For a full list of arguments and details on their use, run the following command.
```
otp-dict-breaker -h
```

### Assumptions
#### CLI/TUI Only
* The common words file is a newline separated, ordered list of most frequently words in English. Not case-sensitive. If unspecified as a CLI argument it uses a built-in list - highly recommended.
* The ciphertexts directory contains a single file (any extension) for each ciphertext and nothing else. Filenames are sorted alphabetically during processing. If unspecified as a positional argument, it uses the current working directory.
* Files that start with `.` (hidden files) are ignored when searching ciphertexts.
* Ciphertexts are formatted as hexadecimal strings (ff, 02, etc.), with bytes seperated by spaces or joined together.

#### For All Modes
* Ciphertexts are a list of strings in hexadecimal format (ff, 02, etc.). Once decrypted, the plaintext bytes all resolve to ASCII characters.
* The common words list is an ordered list of most frequent words in English.
* All ciphertexts have been encrypted with the same OTP key (Many-Time-Pad)
* It is okay if ciphertext lengths are not the same, but they will get truncated to the length of the shortest one.
* The only whitespace character that will appear in the plaintext is a space. Even if this is not the case, we probably can still get a useful decryption output.
* Decimal digits (`0-9`) and some punctuation (`, . " ! ? : ; - " ( )`) may appear in the plaintext. You can disallow them separately using CLI arguments.
* The only single-character words in the plaintexts will be `a` or `i`. We clean up any other words to increase accuracy since a lot of the web-based common-word datasets include most letters on their own. You can disable this behaviour with a CLI argument.
* Instead of the corresponding CLI arguments, you can also use environment variables `OTP_CTXT_DIR_PATH` and `COMMON_WORDS_PATH`. Any CLI arguments passed will always be prioritized above the environment variables.

### Contributing
I built this project in a very short timeframe, and there is still room for improvement (like using NumPy).
It has served its purpose well for me, and I'm publishing it in case it is useful for others as well.

If you find a bug or have any suggestions, please feel free to open up an issue or contribute.
I will be more than happy to answer any questions and help where I can :)

## Credits
Thanks a ton to my professors Tegan Brennan and Alexander Hoover at Stevens Institute of Technology, whose courses I was lucky enough to participate in (CS-396 and CS-579, respectively).
Their lectures and assignments inspired me to build this tiny little project where I got to put the topics I learned in class to practice. The examples ciphertexts included in this
repository are all from my past assignments.

Thanks to my groupmates in CS-579, Archiit Rajanala and Brayden Krus, for their help and inspiration.

The common-words list built-in to this tool was taken directly from https://github.com/first20hours/google-10000-english/blob/master/google-10000-english.txt. The original data is from *Google Web Trillion Word Corpus*.
This data is not to be used for commercial purposes. For details, refer to https://github.com/first20hours/google-10000-english/blob/master/LICENSE.md.

## License
OTP Dictionary Breaker is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

OTP Dictionary Breaker is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with OTP Dictionary Breaker.
If not, see <https://www.gnu.org/licenses/>.

###### Copyright (c) 2026 Mehmet Bertan Tarakçıoğlu, under the AGPL v3.