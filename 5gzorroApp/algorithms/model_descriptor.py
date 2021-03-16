# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 15:05:34 2021

@author: dlaskaratos ICOM
"""

from file.file_manager import FileManager as fm
from config.config import Config as cnf
from exceptions.exceptions import OperationNotRegisteredException

class ModelDescriptor():
    
    registry = None
    
    def init():
        global registry
        registry = {}
    
    def register_pipeline(pipeline_id):
        global registry
        operation_model_list = {}
        registry[pipeline_id] = operation_model_list
        
    def register_model(pipeline_id, model_entity_id, location, version, quality_metrics):
        
        global registry
        new_item = {'id': version, 'quality_metrics': quality_metrics}
        operation_model_list = registry.get(pipeline_id)
        
        if operation_model_list != None:
            if model_entity_id in operation_model_list.keys():
                version_list = operation_model_list.get(model_entity_id)['versions']
                version_list.append(new_item)
            else:
                value = {'location': location, 'versions': [new_item]}
                operation_model_list[model_entity_id] = value
        else:
            raise OperationNotRegisteredException(pipeline_id)
        
    def get_version_path(pipeline_id, model_id):
        global registry
        model = registry.get(pipeline_id).get(model_id)
        location = model.get('location')
        version_list = model.get('versions')
        version = version_list[len(version_list)-1].get('id')
        return str(location)+'/'+version
    
    def to_history():
        global registry
        
    
    def from_history():
        pass
        