# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 11:41:00 2021

@author: dlaskaratos ICOM

Handles the delegation of the requests from the REST Controller by 
constructing an ActivePipeline or modifiying an existing one.

- __active_ops: dictionary containing active pipelines with the execution id as the key

"""

from runtime.active_pipeline import ActivePipeline
import json
import logging

log = logging.getLogger(__name__)


class Handler():
    
    __active_ops = None
    __count = 0
    
    def init():
        global __active_ops
        global __count
         
        __active_ops = {}
        __count = 0
    
    def create_new_pipeline(data):
        global __active_ops
        global __count
        result = None
        status_code = 0
        pipeline_id = data.get('id')
        pipeline = __active_ops.get(pipeline_id)
        if pipeline is not None:
            result = 'Pipeline is already operational.'
            status_code = 409
        else:
             pipeline = ActivePipeline(data.get('id'), 
                                  data.get('_name'), 
                                  data.get('description'), 
                                  data.get('features'), 
                                  data.get('n_steps'), 
                                  data.get('threshold'))
             __active_ops[pipeline.id] = pipeline
             __count = __count + 1
             result = 'Pipeline successfully started.'
             status_code = 200
        return result, status_code
    
    def get_active_pipeline(_id):
        global __active_ops
        pipeline = __active_ops.get(_id)
        return pipeline
    
    def terminate_pipeline(pipeline_id):
        global __active_ops
        global __count
        result = None
        status_code = 0
        pipeline = __active_ops.get(pipeline_id)
        if pipeline is None:
            result = 'Pipeline not found.'
            status_code = 404
        else:
            del __active_ops[pipeline_id]
            __count = __count - 1
            result = 'Pipeline successfully terminated.'
            status_code = 200
        
        return result, status_code
        
    def set_prediction(data):
        global __active_ops
        pipeline_id = data.get('pipeline_id')
        prediction = float(data.get('prediction'))
        timestamp = data.get('timestamp')
        pipeline = Handler.get_active_pipeline(pipeline_id)
        if pipeline is not None:
            pipeline.prediction_for_accuracy = prediction
            pipeline.prediction_date = timestamp
            result = 'Successfully set prediction for ' + pipeline_id
        else:
            result = 'Pipeline not found.'
            
        return result, pipeline, prediction
                
    
    
    def get_active_list():
        global __active_ops
        global __count
        result = None

        # Initialize an empty list
        active_list = {}
        
        if __count < 1:
            result = 'No active pipelines.'
        else:
            for entry in __active_ops:
                pipeline = __active_ops.get(entry)                
                json_object = {'id' : pipeline.id,
                            'name' : pipeline.name,
                            'description' : pipeline.description,
                           }
                active_list[pipeline.id] = json_object
        result = json.dumps(active_list)
        
        return result
    
    def get_pipeline(pipeline_id):
        global __active_ops
        pipeline = __active_ops.get(pipeline_id)
        result = None
        status_code = 0
        if pipeline is not None:
            result = {}
            result['id'] = pipeline.id
            result['name'] = pipeline.name
            result['description'] = pipeline.description
            result = json.dumps(result)
            status_code = 200
        else:
            result = "Pipeline "+"'"+str(pipeline_id)+"' "+"does not exist."
            status_code = 404
        
        return result, status_code
        

