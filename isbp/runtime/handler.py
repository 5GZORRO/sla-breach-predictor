# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 11:41:00 2021

@author: dlaskaratos ICOM

Handles the delegation of the requests from the REST Controller by 
constructing an ActivePipeline or modifiying an existing one.

- __active_ops: dictionary containing active pipelines with the execution id as the key

"""

from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
from runtime.active_pipeline import ActivePipeline
import json
import logging

log = logging.getLogger(__name__)


class Handler():
    
    scaler = None
    __active_ops = None
    __count = 0
    
    def init():
        global __active_ops
        global __count
         
        __active_ops = {}
        __count = 0
    
    def get_list():
        global __active_ops
        return __active_ops
    
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
            transaction_id = data.get('transactionID')
            product_id = data.get('productID')
            resource_id = data.get('resourceID')
            instance_id = data.get('instanceID')
            pipeline = ActivePipeline(transaction_id, 
                                  product_id,
                                  resource_id,
                                  instance_id)
            __active_ops[pipeline.productID] = pipeline
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
        pipeline_id = data.get('slaID')
        prediction = float(data.get('value'))
        timestamp = data.get('datetimeViolation')
        pipeline = Handler.get_active_pipeline(pipeline_id)
        if pipeline is not None:
            pipeline.prediction_for_accuracy = prediction
            pipeline.prediction_date = timestamp
            result = 'Successfully set prediction for ' + pipeline_id
            prediction = Handler.transform(prediction)
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
    
    def init_scaler():
        global scaler
        data = pd.read_csv('train.csv')
        bw = data['bw'].to_numpy()
        scaler = MinMaxScaler(feature_range=(0, 10))
        bw = bw.reshape(-1, 1)
        scaler.fit(bw)
        
    def transform(data):
        global scaler
        data = np.array(data)
        data = data.reshape(-1, 1)
        data = scaler.transform(data)
        data = 100-data
        return round(data[0][0])
    
    def inverse_transform(data):
        global scaler
        data = np.array(data)
        data = data.reshape(-1, 1)
        data = scaler.inverse_transform(data)
        return data[0][0]
        
        
