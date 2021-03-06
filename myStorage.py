#!/usr/bin/env python

import sys, re, os, argparse, uuid, time, json, datetime, pytz
from datetime import datetime

import boto.s3

from boto.s3.connection import S3Connection
from boto.s3.bucket import Bucket
from boto.s3.key import Key 

# http://boto.readthedocs.org/en/latest/sqs_tut.html

parser = argparse.ArgumentParser(description='David Edson\'s you beute bucket testerer')

parser.add_argument('-v', '--verbose', action='store_true', help='show verbose detail')
parser.add_argument('-z', '--zone',    action='store',      help='AWS Region', default=os.environ['AWS_REGION'])
parser.add_argument('-t', '--target',  action='store',      help='Target local directory', default='.buckets')
parser.add_argument('-b', '--bucket',  action='store',      help='The storage bucket name')
parser.add_argument('-y', '--yes',     action='store_true', help='yes to klobber')

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-l', '--list',     action='store_true', help='list all buckets')
group.add_argument('-D', '--dump',     action='store_true', help='dump entire directory of bucket')
group.add_argument('-d', '--dir',      action='store_true', help='directory of bucket')
group.add_argument('-K', '--kinghit',  action='store_true', help='klobber all files in bucket')
group.add_argument('-k', '--klobber',  action='store',      help='klobber file in bucket', nargs='*')
group.add_argument('-g', '--get',      action='store',      help='get file from bucket',   nargs='*')
group.add_argument('-p', '--put',      action='store',      help='put file in bucket',     nargs='*')

args = parser.parse_args()

if args.verbose:
    sys.stderr.write('args:\n')
    json.dump(vars(args), sys.stderr, indent=4)

class MyStorage(object):

    def __init__(self, region, bucket=None, target=None):
        self.conn = boto.s3.connect_to_region(
            region,
            aws_access_key_id=os.environ['AWS_KEY'],
            aws_secret_access_key=os.environ['AWS_SECRET']
        )
        if bucket:
            self.bucket = self.conn.get_bucket(bucket)
            sys.stderr.write('Bucket(%s):\n' % self.bucket.name)
            self.target = '%s/%s/'%(target.rstrip('/'),bucket)
        return

    def __del__(self):
        return

    def list(self):
        for bucket in self.conn.get_all_buckets():
            print bucket.name
        return

    def dir(self):
        sys.stderr.write('Directory\n')
        for key in self.bucket:
            print key.name
        return

    def getFile(self, file):
        key = Key(self.bucket)
        key.key = file
        if not key:
            return
        local = '%s/%s' % (self.target.rstrip('/'), file)
        dir = os.path.dirname(local)
        if not os.path.isdir(dir):
            os.makedirs(dir)
        fp = open(local, 'w')
        key.get_contents_to_file(fp)
        fp.close()
        
        est = pytz.timezone('Australia/Sydney')
        gmt = pytz.timezone('GMT')
        tzf = '%Y-%m-%d %H:%M:%S %Z%z'
        
        #print 'last_modified=', key.last_modified
        dt = datetime.strptime(key.last_modified, "%a, %d %b %Y %H:%M:%S %Z")
        #print 'dt=', dt.strftime(tzf)
        
        dt = gmt.localize(dt)
        adt = est.normalize(dt.astimezone(est))
        #print 'adt=', adt.strftime(tzf)

        t = time.mktime(adt.timetuple())
        os.utime(local,(t,t))

        sys.stdout.write('%s %s\n' %(adt.strftime(tzf),local))
        return
        
    def get(self, files):
        sys.stderr.write('Get\n')
        for file in files:
            self.getFile(file)
        return
    
    def dump(self):
        sys.stderr.write('Dump\n')
        for key in self.bucket:
            self.getFile(key.name)
        return
        
    def put(self, files):
        for file in files:
            sys.stderr.write('Put(%s)\n'%file)
            key = Key(self.bucket)
            target = os.path.abspath(self.target)
            path = os.path.abspath(file)
            if path.startswith(target):
                path = path[len(target)+1:]
            else:
                path = file
            key.key = path
            sys.stdout.write('\t%s\n' % path)
            fp = open(file)
            key.set_contents_from_file(fp)
            fp.close()
        return

    def klobber(self, files):
        sys.stderr.write('Klobber\n')
        for file in files:
            key = Key(self.bucket)
            if not key:
                continue
            key.key = file
            print key.name
            key.delete()
        return

    def kinghit(self):
        sys.stderr.write('Kinghit\n')
        for key in self.bucket:
            print key.name
            key.delete()
        return

def main():
    myStorage = MyStorage(args.zone, args.bucket, args.target)

    if args.list:    myStorage.list()
    if args.dir:     myStorage.dir()
    if args.dump:    myStorage.dump()
    if args.get:     myStorage.get(args.get)
    if args.put:     myStorage.put(args.put)
    if args.klobber: myStorage.klobber(args.klobber)
    
    if args.kinghit:
        if args.yes:
            awooga = 'yes'
        else:
            awooga = raw_input("are you sure ? (yes/no) >")
        if awooga == 'yes':
            myStorage.kinghit()
    
    return

if __name__ == '__main__': main()
