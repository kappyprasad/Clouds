#!/usr/bin/env python

import sys, re, os, argparse, uuid, StringIO, json, xmltodict

import boto.route53

from myAWS import MyObject

# http://boto.readthedocs.org/en/latest/ec2_tut.html

def argue():
    parser = argparse.ArgumentParser(description='David Edson\'s you beute EC2 testerer')

    parser.add_argument('-v', '--verbose',   action='store_true', help='show verbose detail')
    parser.add_argument(      '--awsKey',    action='store',      help='AWS user Key',      default=os.environ['AWS_KEY'])
    parser.add_argument(      '--awsSecret', action='store',      help='AWS secret Key',    default=os.environ['AWS_SECRET'])
    parser.add_argument('-z', '--zone',      action='store',      help='AWS Region',        default=os.environ['AWS_REGION'])
    parser.add_argument('-o', '--output',    action='store',      help='output to file')
    parser.add_argument('-d', '--dir',       action='store_true', help='list of zones')
    parser.add_argument('-t', '--tags',      action='store_true', help='show tags of targets')
    parser.add_argument('-r', '--routes',    action='store',      help='list specific zone')
    
    args = parser.parse_args()
    
    if args.verbose:
        sys.stderr.write('args : %s' % vars(args))
            
    return args

####################################################################################################
class MyRoutes(MyObject):

    region = None
    conn = None
        
    def __init__(self, region, key, access):
        super(MyRoutes,self).__init__(dir=args.dir,tags=args.tags)
        self.region = region
        self.conn = boto.route53.connect_to_region(
            region,
            aws_access_key_id=key,
            aws_secret_access_key=access
        )
        return
        
    def __del__(self):
        self.conn.close()
        return

    def zones(self):
        results = {
            'zones' : {
                'zone' : []
            }
        }
        zones = results['zones']['zone']
        for zone in self.conn.get_zones():
            zones.append({
                '@name'         : '%s'%zone.name,
                '@id'           : '%s'%zone.id,
            })
        return results
    
    def routes(self,zone):
        results = {
            'routes' : {
                'route' : []
            }
        }
        routes = results['routes']['route']
        zone = self.conn.get_zone(zone)
        if not zone:
            return
        for route in zone.get_records():
            jroute = {
                '@name'         : '%s'%route.name,
                '@id'           : '%s'%route.identifier,
                'records'       : xmltodict.parse(route.to_xml()),
            }
            routes.append(jroute)
            self._dir(route,jroute)
            self._tags(route,jroute)
        return results

####################################################################################################
def main():
    global args
    args = argue()
    
    myRoutes = MyRoutes(
        args.zone, 
        args.awsKey, 
        args.awsSecret
    )
    
    if args.output:
        output = open(args.output,'w')
    else:
        output=sys.stdout
    
    if args.routes:
        json.dump(myRoutes.routes(args.routes), output)
    else:
        json.dump(myRoutes.zones(), output)
        
    if args.output:
        print args.output
        output.close()
    return

if __name__ == '__main__': main()
