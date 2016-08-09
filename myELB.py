#!/usr/bin/env python

import sys, re, os, argparse, uuid, StringIO, json

import boto.ec2
import boto.ec2.elb

from myAWS import MyObject

# http://boto.readthedocs.org/en/latest/ec2_tut.html

parser = argparse.ArgumentParser(description='David Edson\'s you beute EC2 testerer')

parser.add_argument('-v', '--verbose',   action='store_true', help='show verbose detail')
parser.add_argument(      '--awsKey',    action='store',      help='AWS user Key',      default=os.environ['AWS_KEY'])
parser.add_argument(      '--awsSecret', action='store',      help='AWS secret Key',    default=os.environ['AWS_SECRET'])
parser.add_argument('-z', '--zone',      action='store',      help='AWS Region',        default=os.environ['AWS_REGION'])
parser.add_argument('-o', '--output',    action='store',      help='output to file')
parser.add_argument('-d', '--dir',       action='store_true', help='full directory listing of targets')
parser.add_argument('-t', '--tags',      action='store_true', help='show tags of targets')
parser.add_argument('-i', '--id',        action='store',      help='id of instance, will be introspected if not provided')

args = parser.parse_args()

if args.verbose:
        sys.stderr.write('args : %s' % vars(args))

############################################################################################################################        
class MyELB(MyObject):
    
    region      = None
    conn        = None

    def __init__(self, region, key, access):
        super(MyELB,self).__init__(dir=args.dir,tags=args.tags)
        
        self.region = region
        self.conn = boto.ec2.elb.connect_to_region(
            region,
            aws_access_key_id=key,
            aws_secret_access_key=access
        )
        return
        
    def __del__(self):
        self.conn.close()
        return

    def _subnets(self,source,target):
        target['subnets'] = {
            'subnet' : []
        }
        subnets = target['subnets']['subnet']
        for sn in source.subnets:
            subnets.append({
                '@id' : '%s'%sn
            })
        return

    def _instances(self,source,target):
        target['instances'] = {
            'instance' : []
        }
        instances = target['instances']['instance']
        for instance in source.instances:
            instances.append({
                '@id' : '%s'%instance.id
            })
            #self.instances.add(instance.id)
        return
        
    def process(self):
        results = {
            'elbs' : {
                'elb' : []
            }
        }
        elbs = results['elbs']['elb']
        
        for lb in self.conn.get_all_load_balancers():
            elb = {
                '@name' : lb.name,
                '@vpc_id' : lb.vpc_id,
                '@dns_name' : lb.dns_name
            }
                
            self._dir(lb,elb)
            self._tags(lb,elb)
            self._subnets(lb,elb)
            self._instances(lb,elb)

            elbs.append(elb)
        
        return results
    
def main():
    myELB = MyELB(
        args.zone, 
        args.awsKey, 
        args.awsSecret
    )
    
    if args.output:
        output = open(args.output,'w')
    else:
        output=sys.stdout

    json.dump(myELB.process(),output)

    if args.output:
        print args.output
        output.close()
    return

if __name__ == '__main__': main()
