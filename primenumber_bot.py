#!/usr/bin/python

import daemon
import logging
import bot

with daemon.DaemonContext():
    logging.basicConfig(filename="/var/log/apps/primenumber_bot.log",level=logging.WARN,
                        format="%(asctime)s:%(message)s")
    bot.botmain()
