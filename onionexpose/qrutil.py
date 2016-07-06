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

import pyqrcode
import math

"""
This file aims to turn a QR code produced by pyqrcode's `text()` method
into something similar to the output of `qrencode -t utf8`, thus
allowing it to take up half the space in each direction and fit on an
80x24 terminal.
"""

class QRMatrix:
    def __init__(self, lines):
        self.lines = lines

    def __getitem__(self, param):
        if type(param) is not tuple:
            raise ValueError("Expected tuple")
        x, y = param
        try:
            return self.lines[x][y] == "1"
        except IndexError:
            return False

    def get_width(self):
        return len(self.lines[0])

    def get_height(self):
        return len(self.lines)

    def get_size(self):
        return get_width(), get_height()

    width = property(get_width)
    height = property(get_height)
    size = property(get_size)

class QRWrapper:
    def __init__(self, data):
        self.matrix = QRMatrix(pyqrcode.create(data, error="L").text().split("\n"))

    def _get_display_char(self, top, bottom):
        if top and bottom:
            return " "
        elif not top and bottom:
            return "\u2580"
        elif not bottom and top:
            return "\u2584"
        elif not bottom and not top:
            return "\u2588"

    def compact_repr(self):
        lines = []
        for i in range(math.floor(self.matrix.height / 2)):
            line = ""
            for j in range(self.matrix.width):
                line += self._get_display_char(self.matrix[j, i * 2], self.matrix[j, i * 2 + 1])
            lines += [line]
        return "\n".join(lines)


if __name__ == "__main__":
    print(QRWrapper("Just for debugging!").compact_repr())
