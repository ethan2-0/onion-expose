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

import threading
import requests
import os
import binascii
from flask import Flask, send_file, request, abort
from config import config

# TODO: We've got a lot of code duplication in here from fileserver.py. Perhaps merge the two, or build some fancy OO something.
# Note to self: ncat -c "ncat --proxy-type socks5 --proxy 127.0.0.1:9050 sx57pqdgpz3x7frb.onion 80" -l 1234

class StatusServerRunThread(threading.Thread):
    def __init__(self, app, port):
        threading.Thread.__init__(self)
        self.app = app
        self.port = port

    def run(self):
        self.app.run(port=self.port)

class StatusServer:
    def __init__(self, port=config.status_port):
        self.port = port
        self.app = Flask(__name__)
        self.nonce = binascii.hexlify(os.urandom(32)).decode("utf8")
        if config.debug:
            print("Status server", self.port, self.nonce)

        @self.app.route("/shutdown")
        def serve_shutdown_wrapper():
            return self.serve_shutdown()

        @self.app.route("/")
        @self.app.route("/<path:path>")
        def serve_info_wrapper(path=""):
            return self.serve_info(path)

    def run(self):
        self.run_thread = StatusServerRunThread(self.app, self.port)
        self.run_thread.start()

    def serve_info(self, path):
        return send_file("infopage_status.html")

    def serve_shutdown(self):
        if config.debug:
            print("Got a shutdown request for statusserver", request.args.get("nonce"))
        if request.args.get("nonce") != self.nonce:
            if config.debug:
                print("Invalid nonce")
            abort(403, "Need the correct nonce.")
        request.environ.get("werkzeug.server.shutdown")()
        return "Doing shutdown."

    def teardown(self):
        if config.debug:
            print("Sending a shutdown request to statusserver")
        requests.get("http://localhost:%s/shutdown" % self.port, params=dict(nonce=self.nonce))
