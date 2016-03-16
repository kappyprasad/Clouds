#!/usr/bin/env python

import sys, re, os, argparse, uuid, json

from Tools.pretty import *

import boto.dynamodb2
from boto.dynamodb2.table import Table
from boto.dynamodb2.results import ResultSet
from boto.dynamodb2.fields import HashKey, RangeKey, AllIndex, KeysOnlyIndex
from boto.dynamodb2.types import STRING, NUMBER

schema = {
    'FirstName' : 'STRING',
    'LastName'  : 'STRING'
}
schemaString = '{ ' + ', '.join(
    map(
        lambda x : '\'%s\' : \'%s\'' % (
            x, schema[x]), schema.keys()
    )
) + ' }'

parser = argparse.ArgumentParser(description='David Edson\'s you beute DB testerer')

parser.add_argument('-v', '--verbose',  action='store_true', help='show verbose detail')
parser.add_argument('-f', '--file',     action='store_true', help='input argument is a file')
parser.add_argument('-o', '--output',   action='store',      help='output to file')
parser.add_argument('-z', '--zone',     action='store',      help='AWS Region of table',   default=os.environ['AWS_REGION'])
parser.add_argument('-t', '--table',    action='store',      help='DynamoDB table',        default='david-edson-mucken')
parser.add_argument(      '--hashkey',  action='store',      help='name of hashkey',       default='dataset')
parser.add_argument(      '--hashval',  action='store',      help='value of hashkey',      default=os.environ['USER'])
parser.add_argument(      '--indexkey', action='store',      help='name of indexkey',      default='document_id')
parser.add_argument('-l', '--list',     action='store_true', help='list tables')
parser.add_argument('-s', '--schema',   action='store_true', help='show schema')
parser.add_argument('-c', '--create',   action='store_true', help='create table')
parser.add_argument('-a', '--all',      action='store_true', help='get all')
parser.add_argument('-g', '--get',      action='store',      help='get row by indexkey',   metavar='key')
parser.add_argument('-i', '--insert',   action='store',      help='insert row',            metavar=schemaString)
parser.add_argument('-q', '--query',    action='store',      help='query rows',            metavar=schemaString)
parser.add_argument('-u', '--update',   action='store',      help='update row',            metavar=schemaString)
parser.add_argument('-r', '--remove',   action='store_true', help='remove row')
parser.add_argument('-d', '--drop',     action='store_true', help='drop table')

args = parser.parse_args()

if args.verbose:
    sys.stderr.write('args:\n')
    prettyPrint(vars(args),colour=True,output=sys.stderr)

class MyDatabase(object):

    def __init__(self, region):
        self.schema = [
            HashKey(args.hashkey,   data_type=STRING),
            RangeKey(args.indexkey, data_type=STRING),
        ]
        self.indexes = [
            AllIndex('FirstName', parts=[
                HashKey(args.hashkey, data_type=STRING),
                RangeKey('FirstName', data_type=STRING),
            ]),
            AllIndex('LastName', parts=[
                HashKey(args.hashkey, data_type=STRING),
                RangeKey('LastName', data_type=STRING),
            ])
        ]
        self.conn = boto.dynamodb2.connect_to_region(
            region,
            aws_access_key_id=os.environ['AWS_KEY'],
            aws_secret_access_key=os.environ['AWS_SECRET']
        )
        return

    def __del__(self):
        return

    def list(self):
        sys.stderr.write('Tables:\n')
        tables = self.conn.list_tables()
        for table in tables['TableNames']:
            sys.stdout.write('%s\n'%table)
        return

    def create(self, name):
        self.table = Table.create(
            name,
            schema=self.schema,
            indexes=self.indexes,
            connection=self.conn
        )
        sys.stdout.write('%s\n'%self.table)
        return

    def all(self):
        query = {
            '%s__eq'%args.hashkey : args.hashval
        }  
        if args.verbose:
            prettyPrint(query, output=sys.stderr,colour=True)
        records = []
        #query['document_id__eq'] = '3e272906-a5df-4a70-b19e-b4e2504525f2'
        for row in self.table.query_2(**query):
            record = {}
            for key in row.keys():
                record[key] = row[key]
            records.append(record)
        return records

    def connect(self, name):
        self.table = Table(
            name,
            connection=self.conn
        )
        sys.stderr.write('Connect: %s\n'%self.table)
        return

    def dbschema(self):
        sys.stderr.write('Schema:\n')
        schema = self.table.describe()
        return schema
        
    def insert(self, dictstring):
        guid = '%s'%uuid.uuid4()
        data = {
            args.hashkey : args.hashval,
            args.indexkey : guid
        }
        for key in dictstring.keys():
            data[key] = dictstring[key]
        if args.verbose:
            prettyPrint(data,colour=True,output=sys.stderr)
        self.table.put_item(data=data)
        return guid

    def query(self):
        return

    def get(self, id):
        sys.stderr.write('Get(%s):\n'%id)
        get = {
            args.hashkey : args.hashval,
            args.indexkey : id
        }
        if args.verbose:
            prettyPrint(get,output=sys.stderr,colour=True)
        doc = self.table.get_item(**get)
        got = {}
        for key in doc.keys():
            got[key] = '%s'%doc.get(key)
        return got

    def update(self):
        return

    def delete(self, name):
        return

    def drop(self, name):
        table = Table(name, connection=self.conn)
        sys.stderr.write('drop=%s\n'%table)
        table.delete()
        return

def main():
    mydb = MyDatabase(args.zone)
    
    if args.list:    mydb.list()
    if args.create:  mydb.create(args.table)

    if args.output:
        output = open(args.output,'w')
    else:
        output = sys.stdout
        
    mydb.connect(args.table)

    if args.all:     
        json.dump(mydb.all(),output)
        
    if args.schema:  
        json.dump(mydb.dbschema(),output)
        
    if args.insert:
        if args.file:
            fp = open(args.insert)
            insert = json.load(fp)
            fp.close()
        else:
            insert = json.loads(args.insert)
        sys.stdout.write('%s\n'%mydb.insert(insert))
        
    if args.get:     
        json.dump(mydb.get(args.get),output)
        
    if args.query:   mydb.query(args.query)
    if args.update:  mydb.update(args.update)
    if args.drop:    mydb.drop(args.table)

    output.close()
    
    return

if __name__ == '__main__': main()
