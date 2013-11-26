#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tweepy
import re

KEYFILE='keys'
        

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


def main():
    auth=getAuth(KEYFILE)
    api=tweepy.API(auth)
    print api.rate_limit_status()
    i=0
    for status in tweepy.Cursor(api.home_timeline,since_id=None).items():
        print status.id, status.id_str
        print status.text
        if i>15:
            break
        i+=1

main()
