#!/usr/bin/python

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

class MyEC2(MyObject):

    region = None
    conn = None
        
    def __init__(self, region, key, access):
        super(MyEC2,self).__init__(dir=args.dir,tags=args.tags)
        self.region = region
        self.conn = boto.ec2.connect_to_region(
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
            'instances' : {
                'instance' : []
            }
        }
        instances = results['instances']['instance']
        for reservation in self.conn.get_all_instances():
            instances.append(self.add(reservation.instances[0]))
        return results

    def find(self,id):
        results = {
            'instances' : {
                'instance' : []
            }
        }
        instances = results['instances']['instance']
        reservations = self.conn.get_all_reservations(instance_ids=[id])
        instances.append(self.add(reservations[0].instances[0]))
        return results
            
    def add(self,instance):
        jnstance = {
            '@name' : '%s'%instance.tags['Name'],
            '@id' : '%s'%instance.id,
            '@ami' : '%s'%instance.image_id,
            '@architecture' : '%s'%instance.architecture,
            '@public_dns' : '%s'%instance.public_dns_name,
            '@type' : '%s'%instance.instance_type,
            '@public_ip' : '%s'%instance.ip_address,
            '@key_name' : '%s'%instance.key_name,
            '@launch_time' : '%s'%instance.launch_time,
            '@private_ip' : '%s'%instance.private_ip_address,
            '@private_dns' : '%s'%instance.private_dns_name,
            '@state' : '%s'%instance.state,
            '@subnet_id' : '%s'%instance.subnet_id,
            '@vpc_id' : '%s'%instance.vpc_id,
        }
        self._dir(instance,jnstance)
        self._tags(instance,jnstance)
        self._interfaces(instance,jnstance)
        return jnstance

def main():
    myEC2 = MyEC2(
        args.zone, 
        args.awsKey, 
        args.awsSecret
    )
    
    if args.output:
        output = open(args.output,'w')
    else:
        output=sys.stdout
    
    if args.id:
        json.dump(myEC2.find(args.id),output)
    else:
        json.dump(myEC2.process(),output)
    
    output.close()
    return

if __name__ == '__main__': main()
