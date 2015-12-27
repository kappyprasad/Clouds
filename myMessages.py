#!/usr/bin/env python

import sys, re, os, argparse, json

from jsonweb.decode import from_object, loader
from jsonweb.encode import to_object, dumper
from jsonweb.schema import ObjectSchema, ValidationError
from jsonweb.validators import String, Integer, Boolean, DateTime, EnsureType, List

import Notifications

options=[]
impt=re.compile('from (\S+) import \*')
path=os.path.dirname(sys.argv[0])
with open('%s/Notifications/__init__.py'%path) as pkg:
    for line in pkg.readlines():
        m = impt.match(line)
        if m:
            options.append(m.group(1))
    pkg.close()
    
parser = argparse.ArgumentParser(description='generated notifications testerer')

parser.add_argument('-v', '--verbose', action='store_true', help='show verbose detail')
parser.add_argument('-t', '--type',    action='store',      help='inject type', required=True, choices=options)

parser.add_argument('file')

args = parser.parse_args()

if args.verbose:
    sys.stderr.write('args:\n')
    json.dump(vars(args), sys.stderr, indent=4)
    sys.stderr.write('\n')
    
def main():
    try:
        fp = open(args.file)
        js = json.load(fp)
        fp.close()
    
        js['__type__'] = args.type
        for key in ['StartTime','Time','EndTime']:
            if key in js.keys():
                js[key]= js[key].replace('Z','000')
        
        if args.verbose:
            sys.stderr.write('json:')
            json.dump(js, sys.stderr, indent=4)
            sys.stderr.write('\n')

        object = loader(json.dumps(js))
        if args.type == 'Message':
            print '{0:<12} {1:<20} {2:<.40} {3:<.40}'.format(
                object.EC2InstanceId, 
                object.Time.strftime(format="%Y-%m-%d %H:%M:%S"),
                object.AutoScalingGroupName, 
                object.Description
            )
        else:
            print dumper(object,indent=4)
    except:
        None
    return

if __name__ == '__main__': main()

