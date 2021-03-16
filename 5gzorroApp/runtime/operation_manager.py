# -*- coding: utf-8 -*-
"""
Created on Wed Mar  3 12:07:26 2021

@author: dlaskaratos
"""
import threading
import ctypes

class OperationManager():
    registry = None
    count = 0
    
    def init():
        global registry
        registry = {}
        
    def register_pipeline(pipeline_id):
        global registry
        operations = {}
        registry[pipeline_id] = operations
    
    def register_operation(pipeline_id, thread):
        global registry
        operations = registry.get(pipeline_id)
        operations[thread.name] = thread
    
    def create_operations(pipeline, models):
        global registry
        threads = None
        if pipeline != None:
            threads = list()
            for model_id in models:
                model = models.get(model_id)
                train_thread = threading.Thread(target = pipeline.start_training, args=(model,))
                predict_thread = threading.Thread(target = pipeline.start_predicting, args=(model,))
                train_thread.name = model.id+'-train'
                predict_thread.name = model.id+'-predict'
                threads.append(train_thread)
                threads.append(predict_thread)
                OperationManager.register_operation(pipeline.id, train_thread)
                OperationManager.count += 1
                OperationManager.register_operation(pipeline.id, predict_thread)
                OperationManager.count += 1
        
        return threads
    
    def start_operations(threads):
        if threads != None:
            for t in threads:
                t.daemon = True
                t.start()
    
    def start_operation_with_id(pipeline, model_id):
        global registry
        # TODO
    
    def terminate_operations(pipeline_id, thread_id = None):
        global registry
        pipeline = registry.get(pipeline_id)
        if pipeline != None:
            if thread_id != None:
                thread = pipeline.get(thread_id)
                res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident,  ctypes.py_object(SystemExit))
                if res > 1:
                    ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, 0)
                else:
                    del pipeline[thread_id]
            else:
                for thread_name in pipeline:
                    thread = pipeline.get(thread_name)
                    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident,  ctypes.py_object(SystemExit))
                    if res > 1:
                        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, 0)
        
        
    def is_active(pipeline_id):
        global registry
        is_active = False
        pipeline = registry.get(pipeline_id)
        if pipeline != None:
            for thread_name in pipeline:
                if pipeline.get(thread_name).is_alive():
                    is_active = True
                    break
        return is_active
        
    
    def get_global_active_count():
        global registry
        counter = 0
        for pipeline in registry:
            for thread_name in registry.get(pipeline):
                if registry.get(pipeline).get(thread_name).is_alive():
                    counter += 1
        
        return counter
    
    def deregister_pipeline(pipeline_id):
        global registry
        del registry[pipeline_id]