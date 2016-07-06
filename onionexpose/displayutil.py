# Copyright (c) 2016, Ethan White
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import curses
import math

def center_pad_text(text, desired_len):
    # See display_fancy_text(...) for explanation pertaining to "\xb2".
    len_needed = desired_len - len(text.replace("\xb2", ""))
    if len_needed <= 0:
        return text
    leftpad = math.floor(len_needed / 2)
    rightpad = math.ceil(len_needed / 2)
    return " " * leftpad + text + " " * rightpad

class WindowWrapper():
    def __init__(self):
        pass

    def init(self):
        self.window = curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self.window.keypad(1)
        self.window.erase()

    def teardown(self):
        self.window.erase()
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        curses.curs_set(1)

    def update_size(self):
        self.height, self.width = self.window.getmaxyx()

    def draw_text(self, text, x, y, attr=0):
        self.window.addstr(y, x, text, attr)

    def draw_fancy_text(self, text, y, x, attr=0):
        """
        Displays text. A unicode `Superscript Two` (U+00B2) toggles bold
        formatting; a unicode `Superscript Three` (U+00B3) toggles
        color inversion. The bold and inversion formatting flags are
        ORed with the `attr` parameter.
        """
        # TODO: Allow formatting other than bold (possibly using other exotic Unicode characters).
        pos = 0
        for i in range(len(text)):
            if text[i] == "\xb2":
                attr ^= curses.A_BOLD
            elif text[i] == "\xb3":
                attr ^= curses.A_REVERSE
            else:
                self.window.addch(y, x + pos, text[i], attr)
                pos += 1

    def refresh(self):
        self.window.refresh()
