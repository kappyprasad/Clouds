#!/usr/bin/python

import re,os,sys,json
from datetime import datetime
from jsonweb.decode import from_object, loader
from jsonweb.encode import to_object, dumper
from jsonweb.schema import ObjectSchema, ValidationError
from jsonweb.validators import String, Integer, Boolean, DateTime, EnsureType, List

#########################################################################################
class AddressSchema(ObjectSchema):
    number = Integer()
    street = String()
    suburb = String()

class JobSchema(ObjectSchema):
    role = String()
    active = Boolean(default=True)
        
class PersonSchema(ObjectSchema):
    id = Integer()
    name = String()
    dob = DateTime(format='%Y-%m-%dT%H:%M:%S')
    title = String(optional=True)
    address = EnsureType("Address")
    jobs = List(EnsureType("Job"))
    
#########################################################################################
@to_object()
@from_object(schema=AddressSchema)
class Address(object):
    def __init__(self,number,street,suburb):
        self.number,self.street,self.suburb = number,street,suburb
        return

@to_object()
@from_object(schema=JobSchema)
class Job(object):
    def __init__(self,role,active):
        self.role,self.active = role,active
        
@to_object()
@from_object(schema=PersonSchema)
class Person(object):
    def __init__(self,id,name,dob,title,address,jobs):
        self.id,self.name,self.dob,self.title,self.address,self.jobs = id,name,dob,title,address,jobs
        return
        
def main():
    address = Address(
        7,
        'Bamboo Av', 
        'Earlwood'
    )
    print 'address='
    js = dumper(address,indent=4)
    print js
    print loader(js)
 
    job = Job('Engineer',True)
    print 'job='
    js = dumper(job,indent=4)
    print js
    print loader(js)
    
    dob=datetime.strptime('1968-08-08 06:00:00', '%Y-%m-%d %H:%M:%S')
    person = Person(
        0,
        'David Edson', 
        dob,
        'Chief Engineer',
        address,
        [job]
    )
    print 'person='
    js = dumper(person,indent=4)
    print js
    other = loader(js)
    print other
    
    print
    addressSchema = AddressSchema()
    print addressSchema, dumper(addressSchema,indent=4)
    jobSchema = JobSchema()
    print jobSchema, dumper(jobSchema,indent=4)
    personSchema = PersonSchema()
    print personSchema, dumper(personSchema,indent=4)
 
    return  

if __name__ == '__main__': main()
