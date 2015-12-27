#!/usr/bin/env python

class Awooga(Exception):

    message = None

    def __init__(self, message):
        self.message = message
        return

def main():
    try:
        a1 = Awooga('hello')
        assert a1
        assert a1.message == 'hello'
        print 'created=%s'%a1.message
        raise a1
    except Awooga as a2:
        assert a2
        assert a2.message == 'hello'
        print 'raised=%s'%a2.message
        
    return
    
if __name__ == '__main__': main()
