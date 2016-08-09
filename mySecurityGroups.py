#!/usr/bin/env python

import sys, re, os, argparse, uuid, StringIO, json, xmltodict

import boto.ec2

from myAWS import MyObject

# http://boto.readthedocs.org/en/latest/ec2_tut.html

def argue():
    parser = argparse.ArgumentParser(description='David Edson\'s you beute EC2 testerer')

    parser.add_argument('-v', '--verbose',   action='store_true', help='show verbose detail')
    parser.add_argument('-i', '--indent',    action='store_true', help='indent content')
    parser.add_argument(      '--awsKey',    action='store',      help='AWS user Key',      default=os.environ['AWS_KEY'])
    parser.add_argument(      '--awsSecret', action='store',      help='AWS secret Key',    default=os.environ['AWS_SECRET'])
    parser.add_argument('-z', '--zone',      action='store',      help='AWS Region',        default=os.environ['AWS_REGION'])
    parser.add_argument('-o', '--output',    action='store',      help='output to file')
    parser.add_argument('-d', '--dir',       action='store_true', help='list of zones')
    parser.add_argument('-t', '--tags',      action='store_true', help='show tags of targets')
    
    args = parser.parse_args()
    
    if args.verbose:
        sys.stderr.write('args : %s' % vars(args))
            
    return args

####################################################################################################
class MySecurityGroups(MyObject):

    region = None
    conn = None
        
    def __init__(self, region, key, access):
        super(MySecurityGroups,self).__init__(dir=args.dir,tags=args.tags)
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

    def sgs(self):
        results = {
            'sgs' : {
                'sg' : []
            }
        }
        sgs = results['sgs']['sg']
        for sg in self.conn.get_all_security_groups():
            jsg = {
                '@name'         : '%s'%sg.name,
                '@id'           : '%s'%sg.id,
                '@vpc_id'       : '%s'%sg.vpc_id,
                '@owner_id'     : '%s'%sg.owner_id,
                '@description'  : '%s'%sg.description,
                'rules'         : self.rules(sg),
            }
            sgs.append(jsg)
            self._dir(sg,jsg)
            self._tags(sg,jsg)
        return results

    def rules(self,sg):
        results = { 'rule' : [] }
        rules = results['rule']
        for rule in sg.rules:
            rules.append({
                '@from_port'    : '%s'%rule.from_port,
                '@to_port'      : '%s'%rule.to_port,
                '@ip_protocol'  : '%s'%rule.ip_protocol,
                '@grants'       : '%s'%rule.grants
            })
        return results

####################################################################################################
def main():
    global args
    args = argue()
    
    myRoutes = MySecurityGroups(
        args.zone, 
        args.awsKey, 
        args.awsSecret
    )
    
    if args.output:
        output = open(args.output,'w')
    else:
        output=sys.stdout
    
    json.dump(myRoutes.sgs(), output, indent=4 if args.indent else None)

    if args.output:
        print args.output
        output.close()
    return

if __name__ == '__main__': main()
