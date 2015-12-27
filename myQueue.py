#!/usr/bin/env python

import sys,re,os,argparse,uuid,time,datetime,json

import boto.sqs
from boto.sqs.message import Message

# http://boto.readthedocs.org/en/latest/sqs_tut.html

parser = argparse.ArgumentParser(description='David Edson\'s you beute SQS testerer')

parser.add_argument('-v', '--verbose', action='store_true', help='show verbose detail')
parser.add_argument('-z', '--zone',    action='store',      help='AWS Region',     default=os.environ['AWS_REGION'])
parser.add_argument('-q', '--queue',   action='store',      help='queue name',     default='%s_Q'%os.environ['USER'])
parser.add_argument('-t', '--timeout', action='store',      help='visibility timeout', default=60, type=int)
parser.add_argument('-b', '--block',   action='store_true', help='block waiting on get')
parser.add_argument('-w', '--wait',    action='store_true', help='wait in a get loop')
parser.add_argument('-o', '--output',  action='store',      help='output directory')

groupA=parser.add_mutually_exclusive_group(required=True)
groupA.add_argument('-l', '--list',    action='store_true', help='list queues')
groupA.add_argument('-c', '--create',  action='store_true', help='create queue')
groupA.add_argument('-p', '--put',     action='store',      help='put message')
groupA.add_argument('-a', '--all',     action='store_true', help='get all messages')
groupA.add_argument('-g', '--get',     action='store_true', help='get message')
groupA.add_argument('-d', '--destroy', action='store_true', help='destroy queue')

args = parser.parse_args()

if args.verbose:
    sys.stderr.write('args : %s' % vars(args))

if 'COLUMNS' in os.environ.keys():
    horizontal = '-'*int(os.environ['COLUMNS'])
else:
    horizontal = '-'*80
    
#########################################################################################
class MyQueue(object):

    def __init__(self, region):
        self.conn = boto.sqs.connect_to_region(
            region,
            aws_access_key_id=os.environ['AWS_KEY'],
            aws_secret_access_key=os.environ['AWS_SECRET']
        )
        self.attrs = {
            'reply_zone': {
                'data_type': 'String',
                'string_value': args.zone
            },
            'reply_queue': {
                'data_type': 'String',
                'string_value': '%s'%uuid.uuid4()
            }
        }
        return

    def __del__(self):
        return

    def list(self):
        queues = self.conn.get_all_queues()
        print queues
        return

    def create(self,queue):
        print 'Create(%s):'%queue
        self.queue = self.conn.create_queue(queue)
        print '\t%s'%self.queue
        return

    def show(self,message):
        js = json.loads(message.get_body())
        if args.output:
            if not os.path.isdir(args.output):
                os.makedirs(args.output)
            file = '%s/%s.json'%(args.output.rstrip('/'),js['MessageId'])
            fp = open(file,'w')
            fp.write(message.get_body())
            fp.close()
            sys.stdout.write('%s\n'%file)
        else:
            sys.stderr.write('\n%s\n'%horizontal)
            sys.stderr.flush()
            print '%s' % message.get_body()
        return

    def get(self, queue):
        print 'Get(%s):' % queue
        self.queue = self.conn.get_queue(queue)
        print '\tQueue=%s' % self.queue
        while args.block:
            message = self.queue.read(visibility_timeout=args.timeout, message_attributes=self.attrs.keys())
            if message:
                self.show(message)
            self.queue.delete_message(message)
            if not args.wait:
                break
            now=datetime.datetime.now()
            sys.stderr.write('\r%s '%now.strftime('%Y-%m-%d %H:%M:%S'))
            time.sleep(1)
        return

    def all(self,queue):
        print 'All(%s):' % queue
        self.queue = self.conn.get_queue(queue)
        print '\tQueue=%s' % self.queue
        print '\tLength=%s' % self.queue.count()
        for i in range(self.queue.count()):
            self.get(queue)
        return
        
        
    def put(self, queue, message):
        print 'Put(%s):' % queue
        self.queue = self.conn.get_queue(queue)
        print '\tQueue=%s' % self.queue
        self.message = Message()
        self.message.message_attributes = self.attrs
        self.message.set_body(message)
        self.queue.write(self.message)
        return

    def destroy(self,queue):
        print 'Destroy(%s)'%queue
        self.queue = self.conn.get_queue(queue)
        print '\tQueue=%s'%self.queu

        self.conn.delete_queue(self.queue)
        return


def main():
    myQ = MyQueue(args.zone)

    if args.list:    myQ.list()
    if args.create:  myQ.create(args.queue)
    if args.put:     myQ.put(args.queue, args.put)
    if args.get:     myQ.get(args.queue)
    if args.all:     myQ.all(args.queue)
    if args.destroy: myQ.destroy(args.queue)

    return

if __name__ == '__main__': main()
