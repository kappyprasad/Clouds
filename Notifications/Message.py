#!/usr/bin/env python

from jsonweb.decode import from_object, loader
from jsonweb.encode import to_object, dumper
from jsonweb.schema import ObjectSchema, ValidationError
from jsonweb.validators import String, Integer, Boolean, DateTime, EnsureType, List, Dict

#########################################################################################
class _Message(ObjectSchema):
    StatusCode           = String()
    AutoScalingGroupARN  = String()
    Description          = String()
    Service              = String()
    Details              = Dict(String())
    AutoScalingGroupName = String()
    ActivityId           = String()
    AccountId            = String()
    RequestId            = String()
    StartTime            = DateTime(format='%Y-%m-%dT%H:%M:%S.%f')
    Time                 = DateTime(format='%Y-%m-%dT%H:%M:%S.%f')
    Progress             = Integer()
    EndTime              = DateTime(format='%Y-%m-%dT%H:%M:%S.%f')
    Cause                = String()
    Event                = String()
    StatusMessage        = String()
    EC2InstanceId        = String()

#########################################################################################
@from_object(schema=_Message)
@to_object()
class Message(object):

    def __init__(self,StatusCode,AutoScalingGroupARN,Description,Service,Details,AutoScalingGroupName,ActivityId,AccountId,RequestId,StartTime,Time,Progress,EndTime,Cause,Event,StatusMessage,EC2InstanceId):
        self.StatusCode           = StatusCode 
        self.AutoScalingGroupARN  = AutoScalingGroupARN 
        self.Description          = Description 
        self.Service              = Service 
        self.Details              = Details 
        self.AutoScalingGroupName = AutoScalingGroupName 
        self.ActivityId           = ActivityId 
        self.AccountId            = AccountId 
        self.RequestId            = RequestId 
        self.StartTime            = StartTime 
        self.Time                 = Time 
        self.Progress             = Progress 
        self.EndTime              = EndTime 
        self.Cause                = Cause 
        self.Event                = Event 
        self.StatusMessage        = StatusMessage 
        self.EC2InstanceId        = EC2InstanceId 
        return
        
