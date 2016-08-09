#!/usr/bin/env python

import sys, re, os, argparse, uuid, StringIO, json

import boto.vpc

from myAWS import MyObject

# http://boto.readthedocs.org/en/latest/ec2_tut.html

def argue():
    parser = argparse.ArgumentParser(description='David Edson\'s you beute vpc testerer')
        
    parser.add_argument('-v', '--verbose',   action='store_true', help='show verbose detail')
    parser.add_argument(      '--awsKey',    action='store',      help='AWS user Key',      default=os.environ['AWS_KEY'])
    parser.add_argument(      '--awsSecret', action='store',      help='AWS secret Key',    default=os.environ['AWS_SECRET'])
    parser.add_argument('-z', '--zone',      action='store',      help='AWS Region',        default=os.environ['AWS_REGION'])
    parser.add_argument('-o', '--output',    action='store',      help='output to file')
    parser.add_argument('-d', '--dir',       action='store_true', help='full directory listing of targets')
    parser.add_argument('-t', '--tags',      action='store_true', help='show tags of targets')
    parser.add_argument('-i', '--id',        action='store',      help='id of vpc, will be introspected if not provided')
    
    args = parser.parse_args()
    
    if args.verbose:
        sys.stderr.write('args : %s' % vars(args))

    return args

class MyVPC(MyObject):

    region = None
    conn = None
        
    def __init__(self, region, key, access):
        super(MyVPC,self).__init__(dir=args.dir,tags=args.tags)
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

    def _interfaces(self,source,target):
        target['interfaces'] = {
            'interface' : []
        }
        interfaces = target['interfaces']['interface']
        for i in source.interfaces:
            interfaces.append({
                '@id' : '%s'%i
            })
        return
    

    def process(self):
        results = {
            'vpcs' : {
                'vpc' : []
            }
        }
        vpcs = results['vpcs']['vpc']
        for vpc in self.conn.get_all_vpcs():
            vpcs.append(self.add(vpc))
        return results

    def find(self,id):
        results = {
            'vpcs' : {
                'vpc' : []
            }
        }
        vpcs = results['vpcs']['vpc']
        reservations = self.conn.get_all_reservations(vpc_ids=[id])
        vpcs.append(self.add(reservations[0].vpcs[0]))
        return results

    def add(self,vpc):
        jvpc = {
            '@cidr_block' : vpc.cidr_block,
            '@id'         : vpc.id,
            '@state'      : vpc.state, 
        }
        self._dir(vpc,jvpc)
        self._tags(vpc,jvpc)
        #self._interfaces(vpc,jvpc)
        return jvpc

def main():
    global args
    args = argue()
    
    myVPC = MyVPC(
        args.zone, 
        args.awsKey, 
        args.awsSecret
    )
    
    if args.output:
        output = open(args.output,'w')
    else:
        output=sys.stdout
    
    if args.id:
        json.dump(myVPC.find(args.id),output)
    else:
        json.dump(myVPC.process(),output)

    if args.output:
        print args.output
        output.close()
    return

if __name__ == '__main__': main()
