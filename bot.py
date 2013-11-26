#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tweepy
import re
import MySQLdb
import prime
import time
import twikey
import logging

class mysqlsetting:
    def __init__(self):
        self.host="localhost"
        self.db="primenumber"
        self.user="primenumberuser"
        self.passwd=""
        

class twitter:
    @staticmethod
    def getAuth():
        auth=tweepy.OAuthHandler(twikey.keys['consumer_key'],
                                 twikey.keys['consumer_secret'])
        auth.set_access_token(twikey.keys['access_token'],
                              twikey.keys['access_token_secret'])
        return auth

    def __init__(self,debug=False,dryrun=False):
        auth=self.getAuth()
        self._api=tweepy.API(auth)
        self._debug=debug
        self._dryrun=dryrun
        self._restricted=False
        self._error=0

    def getTimeline(self,method,limit=100,since_id=None):
        l=[]
        c=0
        try:
            for s in tweepy.Cursor(method,since_id=since_id).items():
                if c>=limit:
                    break
                l.append(s)
                c+=1
            l.reverse()
            self._restricted=False
        except Exception as e:
            self._error=e[0][0]["code"]
            self._restricted=True
            logging.error("** Exception at getting timeline.")
            logging.error(str(e))
        return l
        
    def getMentions(self,limit=100,since_id=None):
        return self.getTimeline(self._api.mentions_timeline,limit,since_id)

    def getHome(self,limit=100,since_id=None):
        return self.getTimeline(self._api.home_timeline,limit,since_id)

    def tweet(self,text,id):
        logging.info("Tweeted: " +text)
        if not self._dryrun:
            try:
                self._api.update_status(text,in_reply_to_status_id=id)
            except Exception as e:
                self._error=e[0][0]["code"]
                logging.error("** Exception at tweeting")
                logging.error(str(e))
                return False
        return True

    def isRestricted(self):
        return self._restricted

    def getErrorCode(self):
        return self._error

class idstore:
    def __init__(self):
        setting=mysqlsetting()
        self._db=MySQLdb.connect(host=setting.host,
                           db=setting.db,
                           user=setting.user,
                           passwd=setting.passwd)
        self._cur=self._db.cursor()

    def get(self):
        self._cur.execute("select id from last")
        r=self._cur.fetchall()
        return r[0][0]

    def set(self,s):
        self._cur.execute("update last set id='%s'" % s)
        self._db.commit()


def getPrime(n):
    if n%2==0:
        n+=1
    while not prime.isPrime(n):
        n+=2
    return n


def botmain(debug=False,dryrun=False):
    tw=twitter(debug=debug,dryrun=dryrun)
    store=idstore()
    while True:
        l=tw.getMentions(since_id=store.get())
        logging.debug("Got %d mentions." % len(l))
        for a in l:
            logging.debug(a.author.screen_name+":"+ a.text)
            t=re.sub("[^0-9]*([0-9]+)[^0-9]*",r'\1',a.text).strip()
            try:
                n=int(t)
                if n<=1:
                    continue
                p=getPrime(n)
                r=tw.tweet("@"+a.author.screen_name+" "+str(p),a.id)
                if r:
                    store.set(a.id)
                    time.sleep(180)
                else:
                    if tw.getErrorCode()==187:
                        store.set(a.id)
            except:
                pass
        if tw.isRestricted:
            time.sleep(180)
        else:
            time.sleep(10)

if __name__=="__main__":
    logging.basicConfig(filename="debug.log",level=logging.DEBUG,
                        format="%(asctime)s:%(message)s")
    botmain(True)
