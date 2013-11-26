#!/usr/bin/python

import daemon
import logging
import bot

with daemon.DaemonContext():
    logging.basicConfig(filename="/var/apps/primenumber_bot.log",level=logging.DEBUG,
                        format="%(ascitime)s:%(message)s")
    bot.botmain()
