#!/usr/bin/env python

import os,re,sys,argparse,json

from troposphere import Ref, Template
import troposphere.ec2

horizon='-'*int(os.environ['COLUMNS'] if 'COLUMNS' in os.environ.keys() else 80)

parser = argparse.ArgumentParser(description='sample app for github.com:cloudtools/troposphere libraries')

parser.add_argument('-v', '--verbose',  action='store_true', help='show verbose detail')

args = parser.parse_args()

if args.verbose:
    sys.stderr.write('args : %s' % vars(args))

def main():
    t = Template()
    
    instance = troposphere.ec2.Instance('myInstance')
    instance.ImageId = 'ami-336c0a09'
    instance.InstanceType = 't1.micro'
    t.add_resource(instance)
    
    print t.to_json(indent=4)
    return

if __name__ == '__main__': main()
