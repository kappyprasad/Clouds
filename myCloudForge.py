#!/usr/bin/env python

import sys,re,os,argparse,uuid,time,datetime,json,urllib

import boto.cloudformation

# http://boto.readthedocs.org/en/latest/ref/cloudformation.html

parser = argparse.ArgumentParser(description='David Edson\'s you beute cloud formerer')

parser.add_argument('-v', '--verbose',       action='store_true', help='show verbose detail')
parser.add_argument('-o', '--output',        action='store',      help='output file')
parser.add_argument('-n', '--name',          action='store',      help='the name of the stack', required=True)

groupA=parser.add_argument_group(description='AWS details')
groupA.add_argument('--awsKey',              action='store',      help='AWS_KEY',    default=os.environ['AWS_KEY'],    metavar='KEY')
groupA.add_argument('--awsSecret',           action='store',      help='AWS_SECRET', default=os.environ['AWS_SECRET'], metavar='SEC')
groupA.add_argument('--zone',                action='store',      help='AWS_REGION', default=os.environ['AWS_REGION'], metavar='REG')

parser.add_argument('file', nargs='*',       action='store',      help='resource file to create')

args = parser.parse_args()

if args.verbose:
    sys.stderr.write('args : ')
    json.dump(vars(args),sys.stderr,indent=4)
    sys.stderr.write('\n')

if 'COLUMNS' in os.environ.keys():
    horizontal = '-'*int(os.environ['COLUMNS'])
else:
    horizontal = '-'*80
    
#########################################################################################
class MyCloudForge(object):
    
    output = None
    conn   = None

    def __init__(self, region, output=sys.stdout):
        self.output = output
        self.conn = boto.cloudformation.connect_to_region(
            region,
            aws_access_key_id=os.environ['AWS_KEY'],
            aws_secret_access_key=os.environ['AWS_SECRET']
        )
        return

    def __del__(self):
        return
    
    def create(self,name,input,output):
        object = json.load(input)
        json.dump(object,output,indent=4)
        output.write('\n')
        output.flush()
        self.conn.create_stack(name,template_body=json.dumps(object))
        return object

def main():
    
    if args.output:
        output = open(args.output,'w')
    else:
        output = sys.stdout
        
    forger = MyCloudForge(args.zone,output=output)
    
    if len(args.file) > 0:
        inputs = map(lambda x : open(x), args.file)
    else:
        inputs = [ sys.stdin ]
        
    sys.stderr.write('%s : \n'%args.name)

    for input in inputs:
        sys.stderr.flush()
        sys.stderr.write('%s\n'%horizontal)
        forger.create(args.name,input,output)
        input.close()
        
    output.close()
    
    return

if __name__ == '__main__': main()
