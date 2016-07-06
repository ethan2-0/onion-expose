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

import yaml
import getpass
import os.path
import socket

defaults = {
    "expose_port": -1,
    "status_port": -1,
    "port_start": 17320,
    "tor_proxy_port": 9050,
    "tor_controller_password": None,
    "debug": False
}

class Config:
    def __init__(self, path=os.path.expanduser("~/.onion-expose.yml")):
        self.path = path
        self.pairs = None

    def _convert_name(self, yamlname):
        return yamlname.replace("-", "_").lower()

    def load(self):
        cfg = None
        if os.path.isfile(self.path):
            with open(self.path) as f:
                # TODO: What if we've got malformed YAML?
                try:
                    cfg = yaml.load(f.read()) # NOTE: Arbitrary code execution. You've been warned.
                except:
                    pass

        if cfg is None:
            cfg = {}

        for key in cfg:
            if self._convert_name(key) == key:
                continue
            cfg[self._convert_name(key)] = cfg[key]
            del cfg[key]

        self.pairs = {}
        for key in defaults:
            self.pairs[key] = cfg.get(key, defaults[key])

        if self.tor_controller_password == None:
            self._prompt_tor_password()

        assert type(self.port_start) is int
        assert type(self.tor_proxy_port) is int
        assert type(self.tor_controller_password) is str

        self._set_ports()

        assert type(self.expose_port) is int
        assert type(self.status_port) is int

    def _prompt_tor_password(self):
        print("I didn't find an entry for 'Tor-Controller-Password' your YAML config file at\n(~/.onion-expose.yml).")
        self.pairs["tor_controller_password"] = getpass.getpass("Enter your Tor controller password (or Ctrl-C and create a config file): ")

    def _try_port(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            sock.connect(("localhost", port))
            sock.close()
            return True
        except:
            return False

    def _set_ports(self):
        print("Finding free ports, hold on...")
        # TODO: We could do a binary search or something here, but I really don't think it's necessary.
        current_port = self.port_start
        while self._try_port(current_port):
            current_port += 2

        self.pairs["start_port"] = current_port
        self.pairs["status_port"] = current_port
        self.pairs["expose_port"] = current_port + 1

    def __getattr__(self, key):
        if self.pairs is None:
            raise ValueError("Using config before initialization")
        if key in self.pairs:
            return self.pairs[key]
        else:
            raise AttributeError(key)

config = Config()
