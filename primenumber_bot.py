#!/usr/bin/python

import daemon
import logging
import bot

with daemon.DaemonContext():
    logging.basicConfig(filename="/var/log/apps/primenumber_bot.log",level=logging.WARN,
                        format="%(asctime)s:%(message)s")
    logging.info("Starting primenumber_bot")
    try:
        bot.botmain()
    except Exception as e:
        logging.error(e.args)
        logging.error(e.message)
    logging.info("Ending primenumber_bot")
        
