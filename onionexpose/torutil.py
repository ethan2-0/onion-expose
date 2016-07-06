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

import stem
import display
import time
import statusserver
import pycurl
import io
import threading
import stem.control
from config import config

controller = None

def setup():
    global controller
    controller = stem.control.Controller.from_port()
    controller.authenticate(password=config.tor_controller_password)

class TunnelStatusPollingThread(threading.Thread):
    def __init__(self, tunnel):
        threading.Thread.__init__(self)
        self.stopped = False
        self.in_contact = False
        self.tunnel = tunnel

    def run(self):
        while not self.stopped:
            if self.in_contact:
                for i in range(20):
                    time.sleep(1)
                    if self.stopped:
                        return
            else:
                time.sleep(2)
                if self.stopped:
                    return
            self.in_contact = self.tunnel.update_status()

class Tunnel:
    def __init__(self, localport, remoteport, exposed_file=None):
        self.localport = localport
        self.remoteport = remoteport
        self.killed = False
        self.exposed_file = exposed_file
        self.is_file_tunnel = self.exposed_file is not None
        self.status_server = statusserver.StatusServer(config.status_port)
        self.polling_thread = TunnelStatusPollingThread(self)

    def create(self):
        self.service = controller.create_ephemeral_hidden_service({
            self.remoteport: self.localport,
            self.status_server.port: self.status_server.port
        })
        self.addr = "%s.onion" % self.service.service_id
        self.start_time = time.time()
        self.status_server.run()
        self.polling_thread.start()
        self.status = "startup"

    def teardown(self):
        controller.remove_ephemeral_hidden_service(self.service.service_id)
        self.status_server.teardown()
        self.polling_thread.stopped = True
        self.killed = True

    def _check_status(self):
        """
        For internal use only. Only members of :class:`Tunnel`
        """
        try:
            output = io.BytesIO()

            query = pycurl.Curl()
            query.setopt(pycurl.URL, "%s:%s" % (self.addr, self.status_server.port))
            query.setopt(pycurl.PROXY, "127.0.0.1")
            query.setopt(pycurl.PROXYPORT, config.tor_proxy_port)
            query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
            query.setopt(pycurl.WRITEFUNCTION, output.write)
            query.perform()

            return "ONIONGROK_CLIENT_STATUS_SUCCESS" in output.getvalue().decode("utf8")
        except Exception as e:
            return False

    def update_status(self):
        is_alive = self._check_status()

        if self.status in ["startup", "down"] and is_alive:
            self.status = "running"

        if self.status == "running" and not is_alive:
            self.status = "down"

        return is_alive

    def get_uptime(self):
        return time.time() - self.start_time

    uptime = property(get_uptime)

def teardown():
    controller.close()
