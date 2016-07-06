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

from config import config
config.load()
import display
import time
import torutil
import argparse
import sys
import os.path
import fileserver
import logging
import io


# Disable logging
logging.basicConfig(level=logging.CRITICAL + 500, stream=io.StringIO())

parser = argparse.ArgumentParser(description="Easily expose ports and files to the public through Tor onion services.")
parser.add_argument("localitem", help="Either (a) a local port number to expose, or (b) a file to expose")
parser.add_argument("--remote-port", metavar="remote-port", help="The remote port that the service will expose", type=int, default=80)

args = parser.parse_args(sys.argv[1:])

localport = -1
remoteport = args.remote_port
expose_file = False
exposed_file = None
file_server = None

if os.path.exists(os.path.realpath(args.localitem)):
    if not os.path.isfile(os.path.realpath(args.localitem)):
        print("onion-expose: error: first argument does exist on the filesystem, but isn't a file. Directories aren't supported yet.")
        sys.exit(-1)
    expose_file = True
    exposed_file = os.path.realpath(args.localitem)
    localport = config.expose_port
else:
    try:
        localport = int(args.localitem)
    except ValueError:
        print("onion-expose: error: first argument doesn't exist on the filesystem, and isn't a number.")
        sys.exit(-1)
    if not 0 < localport < 65536:
        print("onion-expose: error: first argument was a number, but wasn't a valid port")
        sys.exit(-1)

torutil.setup()
tunnel = None

if expose_file:
    file_server = fileserver.FileServer(exposed_file)
    file_server.run()
    tunnel = torutil.Tunnel(localport, remoteport, exposed_file=exposed_file)
else:
    tunnel = torutil.Tunnel(localport, remoteport)

tunnel.create()
if not config.debug:
    display.display_tunnel(tunnel)
else:
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("Ctrl-C detected, exiting the loop...")
            break
        print(tunnel.addr, tunnel.remoteport, tunnel.localport, tunnel.status, tunnel.uptime)

if file_server is not None:
    file_server.teardown()

if config.debug:
    print("Doing tunnel teardown")
tunnel.teardown()
if config.debug:
    print("Tunnel torn down")
    print("Doing torutil teardown")
torutil.teardown()
if config.debug:
    print("Torn down torutil")
