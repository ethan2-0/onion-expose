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

from __future__ import division
import curses
import time
import math
import signal
import qrutil
import displayutil as util
from collections import OrderedDict

def draw_title(addr, localport, remoteport, window):
    center_text = util.center_pad_text("Tunneling \xb2%s\xb2 to \xb2%s\xb2" % ("%s:%s" % (addr, remoteport), "localhost:" + str(localport)), window.width)
    window.draw_fancy_text(center_text, 0, 0, curses.color_pair(1))

def draw_kv(kv, window):
    max_len = max([len(k) for k in kv])
    new_kv = OrderedDict({})
    for key in kv:
        new_key = "%s%s" % (key, " " * (max_len - len(key)))
        new_kv[new_key] = kv[key]
    i = 0
    for key in new_kv:
        window.draw_fancy_text("%s \xb2%s\xb2" % (key, new_kv[key]), i + 2, 1)
        i += 1


def draw_qr(data, window):
    try:
        # TODO: How bad is this for performance?
        lines = qrutil.QRWrapper(data).compact_repr().split("\n")
        # TODO: Having `i` floating here randomly doesn't look good.
        i = 0
        for line in lines:
            y = window.height - len(lines) + i
            x = window.width - len(line)
            window.draw_text(line, x, y)
            i += 1
    except curses.error:
        # TODO: Whyyyyyyyyyyyyyyy
        pass

def draw(tunnel, window):
    window.update_size()
    window.window.clear()
    draw_title(tunnel.addr, tunnel.localport, tunnel.remoteport, window)
    kv = OrderedDict()
    if tunnel.is_file_tunnel:
        kv["Exposed file"] = tunnel.exposed_file
    else:
        kv["Local port"] = str(tunnel.localport)
    kv["Remote host"] = "%s:%s" % (tunnel.addr, tunnel.remoteport)
    kv["Remote HTTP URL"] = "http://%s:%s" % (tunnel.addr, tunnel.remoteport)
    kv["Status"] = {
        "startup": "Startup (unavailable)",
        "running": "Available",
        "down": "Error (unavailable)"
    }[tunnel.status]
    kv["Uptime"] = "%s second(s)" % math.floor(tunnel.uptime) if tunnel.uptime < 60 else \
        "%s minute(s)" % math.floor(tunnel.uptime / 60) if tunnel.uptime < 60*60 else \
        "%s hour(s)" % math.floor(tunnel.uptime / (60*60)) if tunnel.uptime < 60*60*24 else \
        "%s day(s)" % math.floor(tunnel.uptime / (60*60*24))
    draw_kv(kv, window)
    draw_qr("%s:%s" % (tunnel.addr, tunnel.remoteport), window)
    window.refresh()

def display_tunnel(tunnel):
    window = util.WindowWrapper()
    window.init()
    def redraw(arg1=None, arg2=None):
        draw(tunnel, window)
    redraw()
    try:
        while True:
            time.sleep(1)
            redraw()
    except KeyboardInterrupt:
        window.teardown()
        print("Thanks for using onion-expose!")

if __name__ == "__main__":
    starttime = time.time()
    class DummyTunnel:
        def __init__(self):
            self.addr = "facebookcorewwwi.onion"
            self.localport = 8004
            self.remoteport = 80
            self.first_active = 0
        def get_uptime(self):
            return time.time() - starttime
        uptime = property(get_uptime)
        def __getattr__(self, key):
            if key == "active":
                return time.time() - starttime > 5
            raise AttributeError
    window = util.WindowWrapper()
    tunnel = DummyTunnel()
    window.init()
    def redraw(arg1=None, arg2=None):
        draw(tunnel, window)
    redraw()
    try:
        while True:
            # This is actually only one of two update loops.
            # The other redraws information about the hidden service;
            # it's much more periodic.
            time.sleep(1)
            redraw()
    except KeyboardInterrupt:
        window.teardown()
        print("Thanks for using onion-expose!")
