import re
import prime
import time
import logging
import sys
import traceback
import boto3
import configparser
import botocore
import os

import tiny_bsky

BUCKET = "primenumber-bot"
KEY = "bsky-since.txt"


class idstore:
    def __init__(self, filename=None):
        self._filename = filename
        if filename is None:
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
        if self._filename is None:
            r = self._s3_client.get_object(Bucket=BUCKET, Key=KEY)
            body = r["Body"].read()
            return body.decode("utf-8")
        else:
            if not os.path.exists(self._filename):
                return None
            with open(self._filename) as f:
                return f.read()

    def put(self, s):
        if self._filename is None:
            self._s3_client.put_object(
                Bucket=BUCKET, Key=KEY, Body=str(s).encode("utf-8")
            )
        else:
            with open(self._filename, "w") as f:
                f.write(s)


def botmain():
    store = idstore()
    client = tiny_bsky.Client(ini_file="bsky.ini")
    since = store.get()
    l = client.getMentions(since=since)
    for x in l[::-1]:
        text = x["record"]["text"]
        t = re.search(r"-?\d+", text)
        try:
            n = int(t.group())
        except:
            n = None
        if n is not None:
            p = prime.getPrime(n)
            client.post(str(p), uri=x["uri"], cid=x["cid"])
        since = x["record"]["createdAt"]
    store.put(since)


if __name__ == "__main__":
    botmain()
