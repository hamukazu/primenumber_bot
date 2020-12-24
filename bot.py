#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tweepy
import re
import prime
import time
import twikey
import logging
import sys
import traceback
import boto3
import configparser
import botocore


BUCKET = "primenumber-bot"
KEY = "lasttweet.txt"


class twitter:
    @staticmethod
    def getAuth():
        auth = tweepy.OAuthHandler(
            twikey.keys["consumer_key"], twikey.keys["consumer_secret"]
        )
        auth.set_access_token(
            twikey.keys["access_token"], twikey.keys["access_token_secret"]
        )
        return auth

    def __init__(self, debug=False, dryrun=False):
        auth = self.getAuth()
        self._api = tweepy.API(auth)
        self._debug = debug
        self._dryrun = dryrun
        self._restricted = False
        self._error = 0

    def getTimeline(self, method, limit=100, since_id=None):
        l = []
        c = 0
        try:
            if since_id == "" or since_id is None:
                cur = tweepy.Cursor(method)
            else:
                cur = tweepy.Cursor(method, since_id=since_id)
            for s in cur.items():
                if c >= limit:
                    break
                l.append(s)
                c += 1
            l.reverse()
            self._restricted = False
        except Exception as e:
            self._restricted = True
            logging.error("** Exception at getting timeline.")
            logging.error(str(e))
            try:
                self._error = e[0][0]["code"]
                logging.error(self._error)
            except:
                self._error = -1
        return l

    def getMentions(self, limit=100, since_id=None):
        return self.getTimeline(self._api.mentions_timeline, limit, since_id)

    def getHome(self, limit=100, since_id=None):
        return self.getTimeline(self._api.home_timeline, limit, since_id)

    def tweet(self, text, id):
        if not self._dryrun:
            try:
                self._api.update_status(text, in_reply_to_status_id=id)
                logging.info("Tweeted: " + text)
            except Exception as e:
                try:
                    print(type(e))
                    print(e.args[0][0]["code"])
                    self._error = e.args[0][0]["code"]
                except:
                    self._error = -1
                logging.error("** Exception at tweeting")
                logging.error("Tried to tweet: " + text)
                logging.error(str(e))
                return False
        return True

    def isRestricted(self):
        return self._restricted

    def getErrorCode(self):
        return self._error


class idstore:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("aws_credentials")
        AWS_ACCESS_KEY_ID = config["default"]["AWS_ACCESS_KEY_ID"]
        AWS_SECRET_ACCESS_KEY = config["default"]["AWS_SECRET_ACCESS_KEY"]
        sess = sess = boto3.Session(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        self._s3_client = sess.client("s3")

    def get(self):
        r = self._s3_client.get_object(Bucket=BUCKET, Key=KEY)
        body = r["Body"].read()
        return int(body.decode("utf-8"))

    def set(self, s):
        self._s3_client.put_object(Bucket=BUCKET, Key=KEY, Body=str(s).encode("utf-8"))


def botmain(debug=False, dryrun=False):
    tw = twitter(debug=debug, dryrun=dryrun)
    store = idstore()
    failed = 0
    l = tw.getMentions(since_id=store.get())
    logging.debug("Got %d mentions." % len(l))
    for a in l:
        logging.debug(a.author.screen_name + ":" + a.text)
        ss = re.search("-?[0-9]+", a.text)
        if ss is not None:
            i, j = ss.span()
            t = a.text[i:j]
            n = int(t)
            p = prime.getPrime(n)
            repeat = True
            while repeat:
                r = tw.tweet("@" + a.author.screen_name + " " + str(p), a.id)
                repeat = False
                if r:
                    store.set(a.id)
                    time.sleep(0.5)
                else:
                    err = tw.getErrorCode()
                    logging.debug("Error code :%d", err)
                    if err == 186:  # exeed 140 chars
                        r = tw.tweet(
                            "@" + a.author.screen_name + " Sorry, too long to tweet.",
                            a.id,
                        )
                        store.set(a.id)
                    elif err == 187:  # duplicated tweet
                        logging.debug("Duplicated")
                        store.set(a.id)
                    else:
                        time.sleep(10)
                        repeat = True


if __name__ == "__main__":
    logging.basicConfig(
        filename="debug.log", level=logging.DEBUG, format="%(asctime)s:%(message)s"
    )
    botmain(True)
