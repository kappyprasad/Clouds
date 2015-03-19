#!/usr/bin/python

import sys, re, os, argparse, xmltodict, json, yaml

import boto.ec2
import boto.ec2.elb

import requests

from myAWS import MyObject

parser = argparse.ArgumentParser(description='find EC2 configuration data')

parser.add_argument('-v', '--verbose',     action='store_true', help='show verbose detail')

groupA=parser.add_argument_group(description='AWS details')
groupA.add_argument(      '--awsKey',      action='store',      help='AWS_KEY',    default=os.environ['AWS_KEY'], metavar='KEY')
groupA.add_argument(      '--awsSecret',   action='store',      help='AWS_SECRET', default=os.environ['AWS_SECRET'], metavar='SEC')
groupA.add_argument(      '--zone',        action='store',      help='AWS_REGION', default=os.environ['AWS_REGION'], metavar='REG')

groupF=parser.add_argument_group(description='object fields to capture')
groupF.add_argument('-d', '--dir',         action='store_true', help='include dir of object')
groupF.add_argument('-t', '--tags',        action='store_true', help='include tags of object')

parser.add_argument('-I', '--identity',    action='store',      help='instance-id override')
parser.add_argument('-o', '--output',      action='store',      help='output file name')

groupT=parser.add_argument_group(description='output types')
group1=groupT.add_mutually_exclusive_group()
group1.add_argument('-x', '--xml',         action='store_true', help='output xml format')
group1.add_argument('-y', '--yaml',        action='store_true', help='output yaml format')
group1.add_argument('-j', '--json',        action='store_true', help='output json format')

groupS=parser.add_argument_group(description='scope of query')
group2=groupS.add_mutually_exclusive_group(required=True)
group2.add_argument('-m', '--me',          action='store_true', help='find my details')
group2.add_argument('-c', '--colleagues',  action='store_true', help='find my colleagues (in the same VPC)')
group2.add_argument('-e', '--everybody',   action='store_true', help='find everybody')

columns = [
    ('i',  'id',           'id',                 'ID of machine',         12),
    ('n',  'name',         None,                 'name of instance',      30),
    ('s',  'state',        'state',              'instance state',        10),
    ('a',  'private_ip',   'private_ip_address', 'private IP address',    16),
    ('p',  'private_dns',  'private_dns_name',   'private DNS address',   50),
    ('l',  'launch_time',  'launch_time',        'instance started',      25),
    (None, 'ami',          'image_id',           'AMI image ID',          15),
    (None, 'arch',         'architecture',       'hardware type',         10),
    (None, 'type',         'instance_type',      'instance_type',         10),
    (None, 'key_name',     'key_name',           'pem key name',          35),
    (None, 'subnet_id',    'subnet_id',          'subnet id',             17),
    (None, 'vpc_id',       'vpc_id',             'virtual private cloud', 15),
    ('A',  'public_ip',    'ip_address',         'public IP address',     16),
    ('P',  'public_dns',   'public_dns_name',    'public DNS address',    60),
]

groupC=parser.add_argument_group(description='columns to show')
for (short,long,attr,help,size) in columns:
    if short:
        groupC.add_argument('-%s'%short,'--%s'%long,action='store_true',help=help)
    else:
        groupC.add_argument('--%s'%long,action='store_true',help=help)

args = parser.parse_args()

if args.verbose:
        sys.stderr.write('args : %s' % json.dumps(vars(args),indent=4))

def unicode_representer(dumper, uni):
    node = yaml.ScalarNode(tag=u'tag:yaml.org,2002:str', value=uni)
    return node

yaml.add_representer(unicode, unicode_representer)

class Colleagues(MyObject):

    region = None
    conn   = None
    me     = None
        
    def __init__(self, region, key, access):
        super(Colleagues,self).__init__(dir=args.dir,tags=args.tags)
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

    def _results(self):
        results = {
            'instances' : {
                'instance' : []
            }
        }
        instances = results['instances']['instance']
        return (results, instances)
    
    def me(self,id):
        (results, instances) = self._results()
        reservations = self.conn.get_all_reservations(instance_ids=[id])
        self.me = reservations[0].instances[0]
        instances.append(self._add(self.me))
        return results
            
    def colleagues(self):
        (results, instances) = self._results()
        for reservation in self.conn.get_all_instances():
            colleague = reservation.instances[0]
            if self.me.vpc_id == colleague.vpc_id:
                instances.append(self._add(colleague))
        return results
    
    def everybody(self):
        (results, instances) = self._results()
        for reservation in self.conn.get_all_instances():
            colleague = reservation.instances[0]
            instances.append(self._add(colleague))
        return results
        
    def _add(self,instance):
        if 'Name' in instance.tags.keys():
            name = instance.tags['Name']
        else:
            name = instance.id
        jnstance = {
            '@name' : '%s'         % name,
        }
        for (short,long,attr,help,size) in columns:
            if attr:
                value=getattr(instance,attr)
                jnstance['@%s'%long]= value if value else ''
                    
        self._dir(instance,jnstance)
        self._tags(instance,jnstance)
        self._interfaces(instance,jnstance)
        return jnstance

def main():
    colleagues = Colleagues(
        args.zone, 
        args.awsKey, 
        args.awsSecret
    )
    
    if args.output:
        sys.stderr.write('%s\n'%args.output)
        output = open(args.output,'w')
    else:
        output=sys.stdout
    
    if args.identity:
        id=args.identity
    else:
        whoami="http://169.254.169.254/latest/meta-data/instance-id/"
        id=requests.get(url=whoami).content

    me = colleagues.me(id)
    
    if args.me:          object = me
    if args.colleagues:  object = colleagues.colleagues()
    if args.everybody:   object = colleagues.everybody()
    
    if   args.xml:       xmltodict.unparse(object,output=output,pretty=True,indent='    ')
    elif args.yaml:      yaml.dump(object,stream=output,indent=4,default_flow_style=False)
    elif args.json:      json.dump(object,output,indent=4)
    else:
        
        header = []
        for (short,long,attr,help,size) in columns:
            if getattr(args,long):
                formats = '{0:<%d}'%size
                header.append(formats.format(long))
        if len(header) > 0:
            if args.output:
                output.write('%s\n'%''.join(header))
            else:
                sys.stderr.write('%s\n'%''.join(header))
            
        for instance in object['instances']['instance']:
            values = []
            for (short,long,attr,help,size) in columns:
                if getattr(args,long):
                    formats = '{0:<%d}'%size
                    values.append(formats.format(instance['@%s'%long]))
            if len(values) > 0:
                line = '%s'%''.join(values)
                output.write('%s\n'%line.rstrip(' '))
            
    output.close()
    return

if __name__ == '__main__': main()
