#!/usr/bin/env python

import sys,re,os,argparse,uuid,time,datetime,json,urllib

import boto.iam
from __builtin__ import file
from Cheetah.Tests.NameMapper import results

# http://boto.readthedocs.org/en/latest/ref/iam.html

parser = argparse.ArgumentParser(description='David Edson\'s you beute IAM testerer')

parser.add_argument('-v', '--verbose',       action='store_true', help='show verbose detail')
parser.add_argument('-o', '--output',        action='store',      help='output file')

groupA=parser.add_argument_group(description='AWS details')
groupA.add_argument('--awsKey',              action='store',      help='AWS_KEY',    default=os.environ['AWS_KEY'],    metavar='KEY')
groupA.add_argument('--awsSecret',           action='store',      help='AWS_SECRET', default=os.environ['AWS_SECRET'], metavar='SEC')
groupA.add_argument('--zone',                action='store',      help='AWS_REGION', default=os.environ['AWS_REGION'], metavar='REG')

groupB=parser.add_mutually_exclusive_group(required=True)
groupB.add_argument('-t', '--test',          action='store',      help='test the module into dir',                     metavar='dir')
groupB.add_argument(      '--roles',         action='store',      help='list roles by path prefix',                    metavar='prefix')
groupB.add_argument(      '--users',         action='store',      help='list users by path prefix',                    metavar='prefix')
groupB.add_argument(      '--groups',        action='store',      help='list groups by path prefix',                   metavar='prefix')
groupB.add_argument('-r', '--role',          action='store',      help='get role',                                     metavar='role')
groupB.add_argument('-u', '--user',          action='store',      help='get user',                                     metavar='user')
groupB.add_argument('-g', '--group',         action='store',      help='get group',                                    metavar='group')
groupB.add_argument(      '--userGroups',    action='store',      help='get groups a user belongs to',                 metavar='user')
groupB.add_argument('-R', '--userRoles',     action='store',      help='get roles for a user',                         metavar='user')
groupB.add_argument(      '--rolePolicy',    action='store',      help='get policy document for role',                 metavar='role')
groupB.add_argument('-U', '--userPolicies',  action='store',      help='list user policies',                           metavar='user')
groupB.add_argument(      '--userPolicy',    action='store',      help='get a user policy document',                   metavar='user:policy')
groupB.add_argument('-G', '--groupPolicies', action='store',      help='list group policies',                          metavar='group')
groupB.add_argument(      '--groupPolicy',   action='store',      help='get group policy document',                    metavar='group:policy')

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
class MyIAM(object):
    
    output = None
    conn   = None

    def __init__(self, region, output=sys.stdout):
        self.output = output
        self.conn = boto.iam.connect_to_region(
            region,
            aws_access_key_id=os.environ['AWS_KEY'],
            aws_secret_access_key=os.environ['AWS_SECRET']
        )
        return

    def __del__(self):
        return

    def listRoles(self,prefix):
        results = []
        doc = self.conn.list_roles(path_prefix=prefix, max_items=100)
        roles = doc['list_roles_response']['list_roles_result']['roles']
        for role in roles:
            results.append(role['role_name'])
            if args.verbose:
                sys.stderr.write('%s\n'%role['role_name'])
        json.dump(roles,self.output,indent=4)
        return results
    
    def listUsers(self,prefix):
        results = []
        doc = self.conn.get_all_users(path_prefix=prefix)
        users = doc['list_users_response']['list_users_result']['users']
        for user in users:
            results.append(user['user_name'])
            if args.verbose:
                sys.stderr.write('%s\n'%user['user_name'])
        json.dump(users,self.output,indent=4)
        return results
    
    def listGroups(self,prefix):
        results = []
        doc = self.conn.get_all_groups(path_prefix=prefix)
        groups = doc['list_groups_response']['list_groups_result']['groups']
        for group in groups:
            results.append(group['group_name'])
            if args.verbose:
                sys.stderr.write('%s\n'%group['group_name'])
        json.dump(groups,self.output,indent=4)
        return results
    
    def getRole(self,role_name):
        try:
            doc = self.conn.get_role(role_name=role_name)
            role = doc['get_role_response']['get_role_result']['role']
            if args.verbose:
                sys.stderr.write('%s\n'%role['arn'])
            json.dump(role,self.output,indent=4)
            return role
        except:
            return None
    
    def getUser(self,user_name):
        doc = self.conn.get_user(user_name=user_name)
        user = doc['get_user_response']['get_user_result']['user']
        if args.verbose:
            sys.stderr.write('%s\n'%user['arn'])
        json.dump(user,self.output,indent=4)
        return user
    
    def getGroup(self,group_name):
        doc = self.conn.get_group(group_name=group_name)
        group = doc['get_group_response']['get_group_result']['group']
        if args.verbose:
            sys.stderr.write('%s\n'%group['arn'])
        if 'users' in group.keys():
            users = group['users']
            for user in users:
                if args.verbose:
                    sys.stderr.write('%s\n'%user['user_name'])
        json.dump(group,self.output,indent=4)
        return group
    
    def getGroupsForUser(self,user_name):
        results = []
        doc = self.conn.get_groups_for_user(user_name=user_name)
        groups = doc['list_groups_for_user_response']['list_groups_for_user_result']['groups'] 
        for group in groups:
            results.append(group['group_name'])
            if args.verbose:
                sys.stderr.write('%s\n'%group['group_name'])
        json.dump(groups,self.output,indent=4)
        return results
    
    def getRolePolicy(self,role_name):
        doc = self.conn.get_role(role_name=role_name)
        role = doc['get_role_response']['get_role_result']['role']
        policyDoc = json.loads(urllib.unquote(role['assume_role_policy_document']).decode('utf8'))
        if args.verbose:
            json.dump(policyDoc,sys.stderr, indent=4)
        json.dump(policyDoc,self.output,indent=4)
        return policyDoc

    def getUserPolicies(self,user_name):
        results = []
        doc = self.conn.get_all_user_policies(user_name=user_name)
        policies = doc['list_user_policies_response']['list_user_policies_result']['policy_names']
        for policy in policies:
            results.append(policy)
            if args.verbose:
                sys.stderr.write('%s\n'%policy)
        json.dump(policies,self.output,indent=4)
        return results
    
    def getUserPolicy(self,user_name, policy_name):
        doc = self.conn.get_user_policy(user_name=user_name,policy_name=policy_name)
        policy = doc['get_user_policy_response']['get_user_policy_result']['policy_document']
        policyDoc = json.loads(urllib.unquote(policy).decode('utf8'))
        if args.verbose:
            json.dump(policyDoc,sys.stderr, indent=4)
        json.dump(policyDoc,self.output,indent=4)
        return policyDoc
    
    def getGroupPolicies(self,group_name):
        results = []
        doc = self.conn.get_all_group_policies(group_name=group_name)
        policies = doc['list_group_policies_response']['list_group_policies_result']['policy_names']
        for policy in policies:
            results.append(policy)
            if args.verbose:
                sys.stderr.write('%s\n'%policy)
        json.dump(policies,self.output,indent=4)
        return results
    
    def getGroupPolicy(self,group_name,policy_name):
        doc = self.conn.get_group_policy(group_name=group_name, policy_name=policy_name)
        policy = doc['get_group_policy_response']['get_group_policy_result']['policy_document']
        policyDoc = json.loads(urllib.unquote(policy).decode('utf8'))
        if args.verbose:
            json.dump(policyDoc,sys.stderr, indent=4)
        json.dump(policyDoc,self.output,indent=4)
        return policyDoc
    
    def getUserRoles(self, user_name):
        return

class MyTest(object):
    
    myIAM = None
    target = ''
    
    def __init__(self,zone,target):
        self.myIAM = MyIAM(zone,output=sys.stdout)
        self.target = target
        for dir in [
            self.target,
            '%s/users'%self.target,
            '%s/groups'%self.target,
            '%s/roles'%self.target,
        ]:
            if not os.path.isdir(dir):
                os.makedirs(dir)
        return
    
    def roles(self):    
        with open('%s/roles/.json'%self.target,'w') as output:
            sys.stderr.write('Roles\n')
            self.myIAM.output = output
            roles = self.myIAM.listRoles(prefix='/')
            for role in roles:
                sys.stderr.write('\t%s\n'%role)
                rolePath = '%s/roles/%s'%(self.target,role)
                if not os.path.isdir(rolePath):
                    os.makedirs(rolePath) 
                with open('%s/role.json'%rolePath,'w') as file:
                    self.myIAM.output = file
                    self.myIAM.getRole(role_name=role)
                with open('%s/policy.json'%(rolePath),'w') as file:
                    self.myIAM.output = file
                    self.myIAM.getRolePolicy(role_name=role)
        return
    
    def groups(self):        
        with open('%s/groups/.json'%self.target,'w') as output:
            sys.stderr.write('Groups\n')
            self.myIAM.output = output
            groups = self.myIAM.listGroups('/')
            for group in groups:
                sys.stderr.write('\t%s\n'%group)
                groupPath = '%s/groups/%s'%(self.target,group)
                if not os.path.isdir(groupPath):
                    os.makedirs(groupPath)
                with open('%s/.json'%(groupPath),'w') as file:
                    self.myIAM.output = file
                    self.myIAM.getGroup(group_name=group)
                #groups
                policyPath = '%s/policies/'%groupPath
                if not os.path.isdir(policyPath):
                    os.makedirs(policyPath)
                with open('%s/.json'%(policyPath),'w') as file:
                    self.myIAM.output = file
                    policies = self.myIAM.getGroupPolicies(group_name=group)
                    # policies
                    for policy in policies:
                        with open('%s/%s.json'%(policyPath,policy),'w') as fole:
                            self.myIAM.output = fole
                            self.myIAM.getGroupPolicy(group_name=group, policy_name=policy)
        return
    
    def users(self):    
        with open('%s/users/.json'%self.target,'w') as output:
            sys.stderr.write('Users\n')
            self.myIAM.output = output
            users = self.myIAM.listUsers('/')
            for user in users:
                sys.stderr.write('\t%s\n'%user)
                userPath = '%s/users/%s'%(self.target,user)
                if not os.path.isdir(userPath):
                    os.makedirs(userPath)
                with open('%s/.json'%userPath,'w') as file:
                    self.myIAM.output = file
                    self.myIAM.getUser(user_name=user)
                with open(os.devnull,'w') as devnull:
                    self.myIAM.output=devnull
                    groups = self.myIAM.getGroupsForUser(user_name=user)
                    for group in groups:
                        groupPath = '%s/groups/%s/users'%(self.target,group)
                        if not os.path.isdir(groupPath):
                            os.makedirs(groupPath)
                        linkPath='%s/%s.json'%(groupPath,user)
                        relativePath = '../../../../%s/.json'%userPath
                        if not os.path.islink(linkPath):
                            os.symlink(relativePath, linkPath)
                policyPath = '%s/policies/'%userPath
                if not os.path.isdir(policyPath):
                    os.makedirs(policyPath)
                with open('%s/.json'%policyPath,'w') as file:
                    self.myIAM.output = file
                    policies = self.myIAM.getUserPolicies(user_name=user)
                    for policy in policies:
                        with open('%s/%s.json'%(policyPath,policy),'w') as fole:
                            self.myIAM.output = fole
                            self.myIAM.getUserPolicy(user_name=user, policy_name=policy)
        return

def main():
    if args.output:
        output = open(args.output,'w')
    else:
        output = sys.stdout
        
    if args.test:
        test = MyTest(args.zone,args.test)
        test.roles()
        test.groups()
        test.users()
        return

    myIAM = MyIAM(args.zone,output=output)
    
    if args.roles:         myIAM.listRoles(prefix=args.roles)
    if args.users:         myIAM.listUsers(prefix=args.users)
    if args.groups:        myIAM.listGroups(prefix=args.groups)
    if args.role:          myIAM.getRole(role_name=args.role)
    if args.user:          myIAM.getUser(user_name=args.user)
    if args.group:         myIAM.getGroup(group_name=args.group)
    if args.userGroups:    myIAM.getGroupsForUser(user_name=args.userGroups) 
    if args.rolePolicy:    myIAM.getRolePolicy(role_name=args.rolePolicy)
    if args.userPolicies:  myIAM.getUserPolicies(user_name=args.userPolicies)
    if args.groupPolicies: myIAM.getGroupPolicies(group_name=args.groupPolicies)
    if args.userRoles:     myIAM.getUserRoles(user_name=args.userRoles)
    
    if args.userPolicy:
        bits = args.userPolicy.split(':')
        myIAM.getUserPolicy(user_name=bits[0], policy_name=bits[1])
        
    if args.groupPolicy:
        bits = args.groupPolicy.split(':')   
        myIAM.getGroupPolicy(group_name=bits[0], policy_name=bits[1])
    
    return

if __name__ == '__main__': main()
