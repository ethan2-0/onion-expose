# Introducing `onion-expose`

`onion-expose` is a utility that allows one to easily create and control temporary Tor onion services.

`onion-expose` can be used for any sort of TCP traffic, from simple HTTP to Internet radio to Minecraft to SSH servers.
It can also be used to expose individual files and allow you to request them from another computer.

# Why not just use `ngrok`?

`ngrok` is nice. But it requires everything to go through a central authority (a potential security issue), and imposes
artificial restrictions, such as a limit of one TCP tunnel per user. It also doesn't allow you to expose files easily
(you have to set it up yourself).

# Getting started



# Compatibility

`onion-expose` supports _only Python 3_. It will not run on Python 2. It has been tested on Debian 8 "Jessie" with
Python 3.4 and Tor 0.2.7.6. It _should_ run on Windows, OS X, or (Open|Free)BSD, but I haven't tested it.
