#!/usr/bin/python

import daemon
import logging
import bot
import sys
import traceback

with daemon.DaemonContext():
    logging.basicConfig(filename="/var/log/apps/primenumber_bot.log",level=logging.INFO,
                        format="%(asctime)s:%(message)s")
    logging.info("Starting primenumber_bot")
    try:
        bot.botmain()
    except:
        ty,v,tr=sys.exc_info()
        logging.error(v)
        logging.error(traceback.format_tb(tr))
    logging.info("Ending primenumber_bot")

