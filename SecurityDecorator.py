#!/usr/bin/env python

import sys, re, os, argparse

from Security import Enforcer,Awooga

parser = argparse.ArgumentParser(description='Security Checkerer')
parser.add_argument('-v', '--verbose',   action='store_true', help='show verbose detail')
args = parser.parse_args()

if args.verbose:
        sys.stderr.write('args : %s' % vars(args))

enforcer = Enforcer(realm='/')

##############################################################################################################
class MySecureClass(object):
    
    def __init__(self):
        return

    @enforcer.restrict(role='User')
    def doSomethingNormal(self,params):
        return 'params=%s'%params
        
    @enforcer.restrict(role='Admin')
    def doSomethingSecret(self,params):
        return 'params=%s'%params

##############################################################################################################
def main():
    secured = MySecureClass()
    
    try:
        result = secured.doSomethingNormal('params')
        assert result
        print 'secured.doSomethingNormal allowed correctly'
        assert result == 'params=params'
    except Awooga as awooga:
        assert False, 'should not throw Awooga'
        
    try:
        result = secured.doSomethingSecret('params')
        assert False, 'should have thrown an Awooga'
    except Awooga as awooga:
        assert awooga
        assert awooga.message == 'denied access to role=Admin'
        print 'secured.doSomethingSecret restricted correctly'
        
    return

if __name__ == '__main__': main()
