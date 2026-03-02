"""
tui.py
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
from importlib.metadata import version, PackageNotFoundError
from prompt_toolkit import Application
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.margins import ScrollbarMargin
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.filters import Condition
from prompt_toolkit.data_structures import Point


class OTPDictBreakerTUI:
    def __init__(self, breaker):
        """
        :param breaker:
        Make sure to pass an OTPDictBreaker object that has been initialized with
        a valid common words file and ciphertext directory!
        """

        # Define public and private variables
        self.breaker = breaker

        # Stuff to hold the app state
        self._cursor_row = 0
        self._cursor_col = 0

        self._editing = False
        self._replacement_chars = []

        self._rerun_mode = False
        self._rerun_input = ''

        # Set up keyboard shortcuts...
        self.kb = KeyBindings()
        self._setup_keybindings()

    # This will format all according to the current state of the app.
    # It adds the index of the current ciphertext, and adds green, highlighted
    # text "overlays" on top of the original plaintexts when we are editing it
    def _get_formatted_text(self):
        fragments = []

        for row, planintext in enumerate(self.breaker.maybe_plaintexts):
            # Add the plaintext index at the start of each line
            fragments.append(('fg:ansicyan bold', f'[{row:2d}] '))

            for col, char in enumerate(planintext):
                is_cursor = (row == self._cursor_row and col == self._cursor_col)

                if (self._editing and
                        row == self._cursor_row
                        and 0 <= col - self._cursor_col < len(self._replacement_chars)):
                    # Show the characters the user is typing as a colored overlay
                    # before they are accepted.
                    overwrite_chars = self._replacement_chars[col - self._cursor_col]

                    fragments.append(('bg:ansibrightgreen fg:ansiblack', overwrite_chars))
                elif is_cursor:
                    fragments.append(('reverse', char))
                else:
                    # Highlight unknown chars!
                    if char == '#':
                        fragments.append(('fg:ansibrightmagenta', char))
                    else:
                        fragments.append(('', char))
            fragments.append(('', '\n\n'))

        return fragments

    # Make sure the cursor doesn't g out of the screen. We need this for scrolling later...
    def _clamp_cursor(self):
        num_rows = len(self.breaker.maybe_plaintexts)
        if num_rows == 0:
            self._cursor_row = 0
            self._cursor_col = 0
            return
        self._cursor_row = max(0, min(self._cursor_row, num_rows - 1))
        line_len = len(self.breaker.maybe_plaintexts[self._cursor_row])
        self._cursor_col = max(0, min(self._cursor_col, line_len - 1))

    def manual_text_replacement(self, text_index, position, guess):
        """Apply a guess from manual text replacement"""
        if text_index < 0 or text_index >= len(self.breaker.ciphertexts):
            return
        ctxt = self.breaker.ciphertexts[text_index]
        for i, c in enumerate(guess):
            idx = position + i
            if idx < len(ctxt):
                self.breaker.maybe_key[idx] = ctxt[idx] ^ ord(c)
        self.breaker.update_plaintexts()

    # Return the current coordinated of the cursor
    def _get_cursor_position(self):
        prefix_len = len(f'[{self._cursor_row:2d}] ')
        x = prefix_len + self._cursor_col
        y = self._cursor_row * 2
        return Point(x=x, y=y)

    # Define the keyboard shortcuts for the app
    def _setup_keybindings(self):
        normal_mode = Condition(lambda: not self._editing and not self._rerun_mode)
        edit_mode = Condition(lambda: self._editing)
        rerun_mode = Condition(lambda: self._rerun_mode)

        @self.kb.add('c-c')
        def exit_app(event):
            event.app.exit()

        @self.kb.add('q', 'Q', filter=normal_mode)
        def exit_app_kb(event):
            event.app.exit()

        # Arrow keys to navigate within the text.
        @self.kb.add('up', filter=normal_mode)
        def move_up(event):
            self._cursor_row -= 1
            self._clamp_cursor()

        @self.kb.add('down', filter=normal_mode)
        def move_down(event):
            self._cursor_row += 1
            self._clamp_cursor()

        @self.kb.add('left', filter=normal_mode)
        def move_left(event):
            self._cursor_col -= 1
            self._clamp_cursor()

        @self.kb.add('right', filter=normal_mode)
        def move_right(event):
            self._cursor_col += 1
            self._clamp_cursor()

        # These are helpful for people using fancy keyboards
        @self.kb.add('home', filter=normal_mode)
        def move_home(event):
            self._cursor_col = 0

        @self.kb.add('end', filter=normal_mode)
        def move_end(event):
            if self.breaker.maybe_plaintexts:
                self._cursor_col = len(self.breaker.maybe_plaintexts[self._cursor_row]) - 1
            self._clamp_cursor()

        # Ctrl+e starts text replacement mode
        @self.kb.add('c-e', filter=normal_mode)
        def start_manual_replacement(event):
            self._editing = True
            self._replacement_chars = []

        # Ctrl+r re-runs the dictionary attack with the updated guesses
        # This is quite helpful and can accelerate manual entry
        @self.kb.add('c-r', filter=normal_mode)
        def rerun_dict(event):
            self._rerun_mode = True
            self._rerun_input = '10'

        # Confirm manual text replacements with the return key
        @self.kb.add('enter', filter=edit_mode)
        def confirm_manual_replacement(event):
            if self._replacement_chars:
                self.manual_text_replacement(self._cursor_row, self._cursor_col, ''.join(self._replacement_chars))
            self._editing = False
            self._replacement_chars = []
            self._clamp_cursor()

        # Cancel manuel text replacements with the escape key
        @self.kb.add('escape', filter=edit_mode)
        def cancel_manual_replacement(event):
            self._editing = False
            self._replacement_chars = []

        # Delete with backspace during manuel text entry
        @self.kb.add('backspace', filter=edit_mode)
        def manual_replacement_backspace(event):
            if self._replacement_chars:
                self._replacement_chars.pop()

        # Process any other printable keyboard entry as a replacement character
        @self.kb.add('<any>', filter=edit_mode)
        def manual_reaplacement_type(event):
            ch = event.data
            if len(ch) == 1 and (ch.isprintable() or ch == ' '):
                # Don't go past end of line
                end = len(self.breaker.maybe_plaintexts[self._cursor_row])
                if self._cursor_col + len(self._replacement_chars) < end:
                    self._replacement_chars.append(ch)

        # Use the return key to confirm re-running the dictionary attack
        @self.kb.add('enter', filter=rerun_mode)
        def confirm_rerun(event):
            try:
                iters = int(self._rerun_input.strip())
            except ValueError:
                iters = 10
            for _ in range(max(1, iters)):
                self.breaker.update_plaintexts()
                if not self.breaker.apply_dict_guesses():
                    break
            self.breaker.update_plaintexts()
            self._rerun_mode = False
            self._rerun_input = ''
            self._clamp_cursor()

        # Use the escape key to cancel re-running the dictionary attack
        @self.kb.add('escape', filter=rerun_mode)
        def cancel_rerun(event):
            self._rerun_mode = False
            self._rerun_input = ''

        # Use the backspace key to delete mac iteration count input
        @self.kb.add('backspace', filter=rerun_mode)
        def rerun_backspace(event):
            if self._rerun_input:
                self._rerun_input = self._rerun_input[:-1]

        # Use number inputs to append to the max iteration setting
        @self.kb.add('<any>', filter=rerun_mode)
        def rerun_type(event):
            ch = event.data
            if ch.isdigit():
                self._rerun_input += ch

    def _get_status_bar(self):
        if self._editing:
            replacement_preview = ''.join(self._replacement_chars) if self._replacement_chars else '...'
            return f" Text Replacement Mode (Ciphertext Index {self._cursor_row}, Character {self._cursor_col}): \"{replacement_preview}\" | Enter: Apply | Esc: Cancel "
        if self._rerun_mode:
            return f" Maximum Dictionary Attack Iterations: {self._rerun_input} | Enter: Run | Esc: Cancel "

        row = self._cursor_row
        col = self._cursor_col
        char = ' '
        if self.breaker.maybe_plaintexts and row < len(self.breaker.maybe_plaintexts):
            pt = self.breaker.maybe_plaintexts[row]
            if col < len(pt):
                char = pt[col]

        # Pretty colors :)
        return [
            ('', ' '),
            ('bg:ansibrightmagenta fg:ansiblack bold' , f'Ciphertext Index: {row}'),
            ('', ' | '),
            ('bg:ansibrightmagenta fg:ansiblack bold', f'Character Index: {col}'),
            ('', ' | '),
            ('bg:ansibrightmagenta fg:ansiblack bold', f"Character: '{char}'"),
            ('', ' | '),
            ('bg:ansibrightgreen fg:ansiblack bold', 'Ctrl+E: Replace Text'),
            ('', ' | '),
            ('bg:ansibrightcyan fg:ansiblack bold', 'Ctrl+R: Retry Dictionary Attack'),
            ('', ' | '),
            ('bg:ansibrightred fg:ansiblack bold', 'Ctrl+C/Q: Exit'),
            ('', ' '),
        ]

    # Get the correct coloring style for the status bar depending on the mode.
    def _get_status_bar_style(self):
        if self._editing:
            return 'bg:ansibrightgreen fg:ansiblack bold'
        if self._rerun_mode:
            return 'bg:ansibrightcyan fg:ansiblack bold'
        return ''

    def run(self):
        """
        Launch the TUI! Before launching, it will run the OTPDictBreaker attack once and
        allow the user to manually figure out the missing characters. These changes will
        automatically update the key and plaintexts in OTPDictBreaker. The TUI also lets the
        user re-run the attack at any point to try and make the manual labor a little easier.
        """
        self.breaker.try_decipher(print_results=False)

        try:
            human_readable_version__ = version("otp_dict_breaker")
        except PackageNotFoundError:
            human_readable_version__ = "undefined-dev"

        # Build the header
        header_bar = Window(
            content=FormattedTextControl(f' OTP Dictionary Breaker v{human_readable_version__} ', show_cursor=False),
            height=1,
            style='bg:ansibrightmagenta fg:black'
        )

        # Main window
        text_control = FormattedTextControl(
            self._get_formatted_text,
            show_cursor=False,
            focusable=True,
            get_cursor_position=self._get_cursor_position
        )
        text_window = Window(
            content=text_control,
            wrap_lines=False,
            cursorline=False,
            right_margins=[ScrollbarMargin(display_arrows=True)],
        )

        # Status bar
        status_bar = Window(
            content=FormattedTextControl(self._get_status_bar, show_cursor=False),
            height=1,
            style=self._get_status_bar_style
        )

        layout = Layout(HSplit([header_bar, text_window, status_bar]), focused_element=text_window)

        app = Application(
            layout=layout,
            key_bindings=self.kb,
            full_screen=True
        )

        app.run()
        self.breaker.update_plaintexts()