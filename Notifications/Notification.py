#!/usr/bin/env python2.7

from jsonweb.decode import from_object, loader
from jsonweb.encode import to_object, dumper
from jsonweb.schema import ObjectSchema, ValidationError
from jsonweb.validators import String, Integer, Boolean, DateTime, EnsureType, List, Dict

#########################################################################################
class _Notification(ObjectSchema):
    SignatureVersion = String()
    Timestamp        = String()
    Signature        = String()
    Type             = String()
    SigningCertURL   = String()
    MessageId        = String()
    Message          = String()
    UnsubscribeURL   = String()
    TopicArn         = String()
    Subject          = String()

#########################################################################################
@from_object(schema=_Notification)
@to_object()
class Notification(object):

    def __init__(self,SignatureVersion,Timestamp,Signature,Type,SigningCertURL,MessageId,Message,UnsubscribeURL,TopicArn,Subject):
        self.SignatureVersion = SignatureVersion 
        self.Timestamp        = Timestamp 
        self.Signature        = Signature 
        self.Type             = Type 
        self.SigningCertURL   = SigningCertURL 
        self.MessageId        = MessageId 
        self.Message          = Message 
        self.UnsubscribeURL   = UnsubscribeURL 
        self.TopicArn         = TopicArn 
        self.Subject          = Subject 
        return
        
