#!/usr/bin/env python

import sys, re, os, argparse, uuid, StringIO, json

import boto.vpc

from myAWS import MyObject

# http://boto.readthedocs.org/en/latest/ec2_tut.html

parser = argparse.ArgumentParser(description='David Edson\'s you beute subnet testerer')

parser.add_argument('-v', '--verbose',   action='store_true', help='show verbose detail')
parser.add_argument(      '--awsKey',    action='store',      help='AWS user Key',      default=os.environ['AWS_KEY'])
parser.add_argument(      '--awsSecret', action='store',      help='AWS secret Key',    default=os.environ['AWS_SECRET'])
parser.add_argument('-z', '--zone',      action='store',      help='AWS Region',        default=os.environ['AWS_REGION'])
parser.add_argument('-o', '--output',    action='store',      help='output to file')
parser.add_argument('-d', '--dir',       action='store_true', help='full directory listing of targets')
parser.add_argument('-t', '--tags',      action='store_true', help='show tags of targets')

args = parser.parse_args()

if args.verbose:
        sys.stderr.write('args : %s' % vars(args))

class MySubnet(MyObject):

    region = None
    conn = None
        
    def __init__(self, region, key, access):
        super(MySubnet,self).__init__(dir=args.dir,tags=args.tags)
        self.region = region
        self.conn = boto.vpc.connect_to_region(
            region,
            aws_access_key_id=key,
            aws_secret_access_key=access
        )
        return
        
    def __del__(self):
        self.conn.close()
        return

    def process(self):
        results = {
            'subnets' : {
                'subnet' : []
            }
        }
        subnets = results['subnets']['subnet']
        for subnet in self.conn.get_all_subnets():
            subnets.append(self.add(subnet))
        return results

    def add(self,subnet):
        jsubnet = {
            '@id' : '%s'%subnet.id,
            '@vpc_id' : '%s'%subnet.vpc_id,
        }
        self._dir(subnet,jsubnet)
        self._tags(subnet,jsubnet)
        #self._interfaces(subnet,jsubnet)
        return jsubnet

def main():
    mySubnet = MySubnet(
        args.zone, 
        args.awsKey, 
        args.awsSecret
    )
    
    if args.output:
        output = open(args.output,'w')
    else:
        output=sys.stdout
    
    json.dump(mySubnet.process(),output)

    if args.output:
        print args.output
        output.close()
    return

if __name__ == '__main__': main()
