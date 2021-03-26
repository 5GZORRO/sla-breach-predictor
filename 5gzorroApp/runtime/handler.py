# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 11:41:00 2021

@author: dlaskaratos ICOM

Handles the delegation of the requests from the REST Controller by 
constructing an ActivePipeline or modifiying an existing one.

- __active_ops: dictionary containing active pipelines with the execution id as the key

"""
from pydantic import BaseModel
from typing import (List, Optional)
from runtime.active_pipeline import ActivePipeline
from runtime.operation_manager import OperationManager as om
import json
import time
import logging

log = logging.getLogger(__name__)

class ClientData(BaseModel):

    unique_id : str
    model_id : Optional[str]
    operations : Optional[List[dict]]

class Handler():
    
    __active_ops = None
    
    def init():
        global __active_ops
        __active_ops = {}
    
    def create_new_pipeline(data):
        global __active_ops
        rules = data.get('_rules')
        pipeline = ActivePipeline(data.get('id'), data.get('_name'), data.get('description'), rules)
        __active_ops[pipeline.id] = pipeline
        om.register_pipeline(pipeline.id)
        return pipeline
    
    def get_active_pipeline(_id):
        global __active_ops
        pipeline = __active_ops.get(_id)
        return pipeline
    
    # def get_or_create(data: ClientData):
    #     global __active_ops
    #     pipeline = __active_ops.get(data.unique_id)
    #     if pipeline is None:
    #         pipeline = ActivePipeline(data.unique_id, data.operations)
    #         __active_ops[data.unique_id] = pipeline
    #         om.register_pipeline(pipeline.id)
    #     return pipeline
    
    def start_pipeline(pipeline):
        threads_list = None
        try:
            threads_list = om.create_operations(pipeline, pipeline.models)
            om.start_operations(threads_list)
            result = 'Service started'
        except Exception as e:
            result = 'Error during the start of operations: ' + str(e)
            om.deregister_pipeline(pipeline.id)
        finally:
            del threads_list
        
        return result
    
    def configure_algorithm(pipeline, data):
        pipeline.set_active_training(False)
        pipeline.set_active_prediction(False)
        try:
            pipeline.get_train_thread.join()
            pipeline.get_prediction_thread.join()
            pipeline.update_model(data.model_data)
            pipeline.set_model_available(False)
            pipeline.set_new_model(False)
            Handler.start_pipeline(pipeline)
        except Exception as e:
            print(e)
        
    
    def remove_pipeline(pipeline_id):
        global __active_ops
        del __active_ops[pipeline_id]
    
    def terminate(pipeline_id, thread_id = None, clean_up = True):
        result = None
        try:
            om.terminate_operations(pipeline_id, thread_id)
            result = 'Termination was sucessful.'
        except Exception as e:
            result = str(e)
            log.error(result)
            
        if clean_up:
           
            try:
                om.deregister_pipeline(pipeline_id)
                Handler.remove_pipeline(pipeline_id)
                # TODO: ModelDescriptor to_history
            except Exception as e:
                result = str(e)
                log.error(result)
        
        return result
    
    def update_pipeline(data):
        global __active_ops
        pipeline_id = data['id']
        updates = data['updates']
        pipeline = __active_ops.get(pipeline_id)
        result = None
        if pipeline != None: 
            for update in updates:
                update_type = update['update_type']
                model = pipeline.models.get(update['model_id'])
                threshold = int(update['threshold'])
                metric = update['metric']
                if update_type == 'remove':
                    pass
                elif update_type == 'update':
                    if metric is not None: # Threads need to be restarted
                        predict_thread_id = model.id+'-predict'
                        train_thread_id = model.id+'-train'
                        model.active_prediction = False
                        termination_result = Handler.terminate(pipeline.id, thread_id = predict_thread_id, clean_up = False)
                        time.sleep(1) # wait one second to stop thread asynchronously before restarting
                        model.active_training = False
                        termination_result = Handler.terminate(pipeline.id, thread_id = train_thread_id, clean_up = False)
                        time.sleep(1) # wait one second to stop thread asynchronously before restarting
                        result = 'Terminated threads with status: '+termination_result
                        try:
                            model.metric = metric
                            model.threshold = threshold
                            # om.start_operation_with_id(pipeline, model, thread_id)
                            result = 'Sucessfully restarted prediction thread'
                        except Exception as e:
                            result = str(e)
                            log.error(result)
                    else:
                        model.threshold = threshold
                        
        else:
            result = "Pipeline "+"'"+pipeline_id+"' "+"does not exist."
        
        return 'Update status: '+result
    
    
    def get_active_list():
        global __active_ops
        
        # Initialize an empty list
        active_list = {}
        
        for entry in __active_ops:
            pipeline = __active_ops.get(entry)
            operations = pipeline.models
            op_list = list()
            for operation_id in operations:
                op = {}
                operation = pipeline.models.get(operation_id)
                op['id'] = operation.id
                op['metric'] = operation.metric
                op['threshold'] = operation.threshold
                op['algorithm'] = operation.base
                op['type'] = operation.name
                op_list.append(op)
                
            json_object = {'name' : pipeline.name,
                           'description' : pipeline.description,
                           'operations' : op_list
                           }
            active_list[pipeline.id] = json_object
        
        return json.dumps(active_list)
    
    def get_pipeline(pipeline_id):
        global __active_ops
        pipeline = __active_ops.get(pipeline_id)
        if pipeline is not None:
            result = {}
            result['id'] = pipeline.id
            operations = list()
            for model_id in pipeline.models:
                operation = {}
                model_entity = pipeline.models.get(model_id)
                operation['model_id'] = model_entity.id
                operation['algorithm'] = model_entity.base.upper() + '-'+ model_entity.name.upper()
                operation['metric'] = model_entity.metric
                operation['threshold'] = model_entity.threshold
                operations.append(operation)
            result['operations'] = operations
            result = json.dumps(result)
        else:
            result = "Pipeline "+"'"+str(pipeline_id)+"' "+"does not exist."
        
        return result
        

