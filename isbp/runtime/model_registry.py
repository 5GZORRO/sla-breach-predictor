# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 16:22:13 2022

@author: dlaskaratos
"""

import logging

log = logging.getLogger(__name__)

class Model():
    
    def __init__(self, _name, _metric, _class, _lib):
        self.__id = None
        self.__name = _name
        self.__metric = _metric
        self.__class = _class
        self.__download = True
        self.__lib = _lib
    
    @property
    def _id(self):
        return self.__id
    
    @_id.setter
    def _id(self, value):
        self.__id = value
    
    @property
    def name(self):
        return self.__name
    
    @property
    def metric(self):
        return self.__metric
    
    @property
    def _class(self):
        return self.__class
    
    @property
    def download(self):
        return self.__download
    
    @download.setter
    def download(self, value):
        self.__download = value
    
    @property
    def lib(self):
        return self.__lib
        

class ModelRegistry():
    
    __registry = None
    
    def init():
        global __registry
        __registry = {}
    
    def get(model_id):
        global __registry
        return __registry.get(model_id)
    
    def register_model(model: Model):
        global __registry
        
        try:
            __registry[model._id] = {model}
            log.info('Model {0} successuflly registered'.format(model.name))
        except Exception as e:
            log.error('Error registering model: {0}'.format(e))
    
    def deregister_model(model_id):
        global __registry
        del __registry[model_id]
    
