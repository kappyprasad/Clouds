#!/usr/bin/env python

import sys, re, os, argparse, json, yaml, xmltodict, uuid, time, pytz
from datetime import datetime
from smtplib import LMTP

parser = argparse.ArgumentParser(description='David Edson\'s you beute bucket testerer')

parser.add_argument('-v', '--verbose', action='store_true', help='show verbose detail')
parser.add_argument('-t', '--time',    action='store',      help='datetime.strftime', default='%Y-%m-%d %H:%M:%S %Z')

args = parser.parse_args()

if args.verbose:
    sys.stderr.write('args:\n')
    json.dump(vars(args), output=sys.stderr, indent=4)

def main():

    lmt = os.path.getmtime(sys.argv[0]) 
    print 'lmt=%s'%lmt
    
    est = pytz.timezone('Australia/Sydney')
    gmt = pytz.timezone('GMT')
    tzf = '%Y-%m-%d %H:%M:%S %Z%z'
    
    gdt = datetime.utcfromtimestamp(lmt)
    print 'gdt=', gdt.strftime(tzf)
    
    gdt = gmt.localize(gdt)
    adt = est.normalize(gdt.astimezone(est))
    print 'adt=', adt.strftime(tzf)

    #how to set the file time
    #t = time.mktime(adt.timetuple())
    #os.utime(local,(t,t))

    
    return

if __name__ == '__main__': main()

