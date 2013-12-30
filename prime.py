#!/usr/bin/env python

import sys
import random


SMALL_PRIMES=[]
LIMIT_SMALL_PRIMES=100


def prepare():
    f=[True]*LIMIT_SMALL_PRIMES
    for i in xrange(2,LIMIT_SMALL_PRIMES):
        if f[i]:
            SMALL_PRIMES.append(i)
            j=i
            while j<LIMIT_SMALL_PRIMES:
                f[j]=False
                j+=i


def probPrime(n,a,d,s):
    x=pow(a,d,n)
    if x==1:
        return True
    else:
        for i in xrange(s):
            if x==n-1:
                return True
            x=(x*x)%n
        return False


def isPrime(n):
    for m in SMALL_PRIMES:
        if m*m>n:
            return True
        if n%m==0:
            return False
    s=0
    d=n-1
    # decomposition so that n=2^s d
    while d%2==0:
        d=d/2
        s+=1
    for _ in xrange(100):
        if not probPrime(n,random.randrange(2,n),d,s):
            return False
    return True


def getPrime(n):
    if n<=2:
        return 2
    if n%2==0:
        n+=1
    while not isPrime(n):
        n+=2
    return n



def main():
    if len(sys.argv)<3:
        print "Usage"
        return
    n1=int(sys.argv[1])
    n2=int(sys.argv[2])
    if n1%2==0:
        n1+=1
    while n1<n2:
        if isPrime(n1):
            print n1
        n1+=2

prepare()

if __name__=='__main__':
    main()
