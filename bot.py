#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tweepy
import re
import MySQLdb
import prime
import time


KEYFILE='keys'

class mysqlsetting:
    def __init__(self):
        self.host="localhost"
        self.db="primenumber"
        self.user="primenumberuser"
        self.passwd=""
        

class twitter:
    @staticmethod
    def getAuth(key):
        keys={}
        for l in open(key):
            ll=re.sub('#.*','',l)
            a=ll.split(':')
            if len(a)>=2:
                keys[a[0].strip().lower()]=a[1].strip()
        auth=tweepy.OAuthHandler(keys['consumer_key'],keys['consumer_secret'])
        auth.set_access_token(keys['access_token'],keys['access_token_secret'])
        return auth

    def __init__(self,key,debug=False,dryrun=False):
        auth=self.getAuth(key)
        self._api=tweepy.API(auth)
        self._debug=debug
        self._dryrun=dryrun
        self._restricted=False
        self._error=0

    def getTimeline(self,method,limit=100,since_id=None):
        l=[]
        c=0
        try:
            for s in tweepy.Cursor(method,sinse_id=since_id).items():
                if c>=limit:
                    break
                l.append(s)
                c+=1
            l.reverse()
            self._restricted=False
        except Exception as e:
            print e[0]
            self._error=e[0][0]["code"]
            self._restricted=True
            if self._debug:
                print "** Exception at getting timeline."
                print e
        return l
        
    def getMentions(self,limit=100,since_id=None):
        return self.getTimeline(self._api.mentions_timeline,limit,since_id)

    def getHome(self,limit=100,since_id=None):
        return self.getTimeline(self._api.home_timeline,limit,since_id)

    def tweet(self,text,id):
        if self._debug:
            if id:
                print "In-reply-to %s:" % id,
            print text
        if not self._dryrun:
            try:
                self._api.update_status(text,in_reply_to_status_id=id)
            except Exception as e:
                print e[0]
                self._error=e[0][0]["code"]
                if self._debug:
                    print "** Exception at tweeting"
                    print e
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
        print "update"
        self._cur.execute("update last set id='%s'" % s)
        self._db.commit()


def getPrime(n):
    if n%2==0:
        n+=1
    while not prime.isPrime(n):
        n+=2
    return n


def botmain(debug=False,dryrun=False):
    tw=twitter(KEYFILE,debug=debug,dryrun=dryrun)
    store=idstore()
    while True:
        print store.get()
        l=tw.getMentions(since_id=store.get())
        if debug:
            print "Got %d mentions." % len(l)
        for a in l:
            print a.author.screen_name
            print a.text
            t=re.sub("@[^ ]*","",a.text).strip()
            try:
                n=int(t)
                if n<=1:
                    continue
                p=getPrime(n)
                r=tw.tweet("@"+a.author.screen_name+" "+str(p),a.id)
                print r
                if r:
                    store.put(a.id)
                    time.sleep(180)
                else:
                    if tw.getErrorCode()==187:
                        store.put(a.id)
            except:
                pass
        if tw.isRestricted:
            time.sleep(180)
        else:
            time.sleep(10)

if __name__=="__main__":
    botmain(True)
