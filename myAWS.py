#!/usr/bin/python

import sys, re, os

class MyObject(object):

    def __init__(self,dir=False,tags=False):
        self.dir = dir
        self.tags = tags
        return
        
    def _dir(self,source,target):
        if not self.dir:
            return
        target['dirs'] = {
            'dir' : []
        } 
        dirs=target['dirs']['dir']
        for key in dir(source):
            text = '%s'%getattr(source,key)
            dirs.append({
                '@name' : '%s'%key,
                '#text' : text.replace('\n','\\n')
            })
        return
        
    def _tags(self,source,target):
        if not self.tags:
            return
        if not 'tags' in dir(source):
            return
        target['tags'] = {
            'tag' : []
        }
        tags=target['tags']['tag']
        for tag in source.tags:
            text = '%s'%source.tags[tag]
            tags.append({
                '@name' : '%s'%tag,
                '#text' : text.replace('\n','\\n')
            })
        return
    
