#!/usr/bin/env python2.7

import os,re,sys

from functools import wraps

import Security.Awooga

class Enforcer(object):

    realm = '/'
    tokenCache = {
        # token : Enforcer
    }
    
    def __init__(self,realm='/'):
        self.realm = realm
        # initilise access to openam REST server for querying and caching permissions
        return
    
    def restrict(self,role):
        def actualWrapper(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                sys.stderr.write('realm=%s, role=%s\n'%(self.realm,role))
                allowed = True
                # do some checking here.
                if role == 'Admin':
                    allowed = False
                if role == 'User':
                    allowed = True
                # done
                if not allowed:
                    raise Security.Awooga('denied access to role=%s'%role)
                return f(*args,**kwargs)
            return wrapper
        return actualWrapper

