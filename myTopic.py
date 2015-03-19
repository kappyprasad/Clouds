#!/usr/bin/python

import sys,re,os,argparse,uuid,time,datetime,json

from StringIO import StringIO

import boto.sns

# http://boto.readthedocs.org/en/latest/sqs_tut.html
#############################################################################################################################
class SmartFormatter(argparse.HelpFormatter):

    def _format_action(self, action):
        if action.choices:
            s = StringIO()
            f = '  {0:<%d} {1}'%(self._max_help_position-3)
            s.write(f.format(', '.join(action.option_strings),action.help))
            s.write('\n  {\n')
            s.write(',\n'.join(map(lambda x : '    %s'%x, action.choices)))
            s.write('\n  }\n')
            return s.getvalue()
        # determine the required width and the entry label
        return argparse.HelpFormatter._format_action(self, action) # determine the required width and the entry label
    
#############################################################################################################################
parser = argparse.ArgumentParser(description='David Edson\'s you beute SNS testerer',formatter_class=SmartFormatter)

parser.add_argument('-v', '--verbose',     action='store_true', help='show verbose detail')
parser.add_argument('-z', '--zone',        action='store',      help='AWS Region',     default=os.environ['AWS_REGION'])
parser.add_argument('-t', '--topic',       action='store',      help='topic name',     default='%s_Q'%os.environ['USER'])
parser.add_argument('-o', '--output',      action='store',      help='output directory')

protocols = ['email','email-json','http','https','sqs','sms','application']

parser.add_argument('-P', '--protocol',    action='store',      help='subscribe protocol', choices=protocols, default=protocols[0])

groupA=parser.add_mutually_exclusive_group(required=True)
groupA.add_argument('-l', '--list',        action='store_true', help='list topics')
groupA.add_argument('-c', '--create',      action='store_true', help='create topic')
groupA.add_argument('-p', '--publish',     action='store',      help='pubish message, prefix of @ means a file')
groupA.add_argument('-d', '--destroy',     action='store_true', help='destroy topic')

groupA.add_argument('-s', '--subscribe',   action='store',      help='subscribe to topic',   metavar='endpoint')
groupA.add_argument('-u', '--unsubscribe', action='store',      help='unsubscribe to topic', metavar='endpoint')


args = parser.parse_args()

if args.verbose:
    sys.stderr.write('args : %s' % vars(args))

if 'COLUMNS' in os.environ.keys():
    horizontal = '-'*int(os.environ['COLUMNS'])
else:
    horizontal = '-'*80
    
#########################################################################################
class MyTopic(object):

    def __init__(self, region):
        self.conn = boto.sns.connect_to_region(
            region,
            aws_access_key_id=os.environ['AWS_KEY'],
            aws_secret_access_key=os.environ['AWS_SECRET']
        )
        return

    def __del__(self):
        return

    def list(self,output):
        doc = self.conn.get_all_topics()
        topics = doc['ListTopicsResponse']['ListTopicsResult']['Topics']
        for topic in topics:
            sys.stdout.write('%s\n'%topic['TopicArn'])
        return list

    def create(self,topic,output):
        print 'Create(%s):'%topic
        doc = self.conn.create_topic(topic)
        json.dump(doc,output,indent=4)
        return

    def publish(self, topic, input):
        print 'Put(%s):' % topic
        pattern = re.compile('^@(.*)$')
        match = pattern.match(input)
        if match:
            input = open(match.group(1))
            message = ''.join(input.readlines())
            input.close()
        else:
            message = input
        self.conn.publish(topic=topic,message=message)
        return

    def subscribe(self,topic,endpoint,protocol):
        self.conn.subscribe(topic=topic,protocol=protocol,endpoint=endpoint)
        return
    
    def unsubscribe(self,topic,queue):
        return
    
    def destroy(self,topic,output):
        print 'Destroy(%s)'%topic
        doc = self.conn.delete_topic(topic)
        json.dump(doc,output,indent=4)
        return doc


def main():
    
    if args.output:
        output = open(args.output,'w')
    else:
        output = sys.stdout
    
    myQ = MyTopic(args.zone)

    if args.list:        myQ.list(output)
    if args.create:      myQ.create(args.topic,output)
    if args.publish:     myQ.publish(args.topic, args.publish)
    if args.subscribe:   myQ.subscribe(args.topic,args.subscribe,args.protocol)
    if args.unsubscribe: myQ.unsucsribe(args.topic,args.unsubscribe)
    if args.destroy:     myQ.destroy(args.topic,output)

    output.close()
    return

if __name__ == '__main__': main()
