# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 11:41:00 2021

@author: dlaskaratos ICOM

Handles the delegation of the requests from the REST Controller by 
constructing an ActivePipeline or modifiying an existing one.

- __active_ops: dictionary containing active pipelines with the execution id as the key

"""

from runtime.active_pipeline import ActivePipeline
from runtime.http_connectors import register_pipeline, get_sla_details
from runtime.model_registry import Model, ModelRegistry
from minio import Minio
from minio.error import S3Error
import json
import logging
from configparser import ConfigParser

log = logging.getLogger(__name__)


class Handler():
    
    __active_ops = None
    __parser = None
    __count = 0
    
    def init():
        global __active_ops
        global __count
        global __parser
         
        __active_ops = {}
        __count = 0
        __parser = ConfigParser()
        Handler.__registry_init__()
    
    def get_list():
        global __active_ops
        return __active_ops
    
    def create_new_pipeline(data):
        global __active_ops
        global __count
        transactionID = data.get('transactionID')
        productID = data.get('productID')
        instanceID = data.get('instanceID')
        location = data.get('place')
        pipeline = __active_ops.get(transactionID)
        if pipeline is not None:
            log.info('Pipeline already exists')
            status = 'Pipeline already exists'
        else:
            try:
                sla_details, status = get_sla_details(productID)
                if sla_details is not None:
                    rule = sla_details.get('rule')[0]
                    threshold = float(rule.get('referenceValue'))
                    operator = rule.get('operator')
                    metric_name = rule.get('metric')
                    pipeline = ActivePipeline(transactionID, instanceID, productID, threshold, metric_name, operator, location)
                    __active_ops[pipeline.transactionID] = pipeline
                    __count = __count + 1
                    log.info('Created new pipeline with transactionID: {0}'.format(pipeline.transactionID))
                    register_pipeline(pipeline.transactionID)
                else:
                    log.info('SLA with transactionID {0} could not be retrieved'.format(transactionID))    
            except Exception as e:
                log.info('Error: {0}'.format(str(e)))
        return pipeline
    
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
        pipeline_id = data.get('transactionID')
        prediction = float(data.get('value'))
        timestamp = data.get('datetimeViolation')
        pipeline = Handler.get_active_pipeline(pipeline_id)
        if pipeline is not None:
            pipeline.prediction_for_accuracy = prediction
            pipeline.prediction_date = timestamp
            result = 'Successfully set prediction for ' + pipeline_id
            #prediction = Handler.transform(prediction)
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
                json_object = {'id' : pipeline.transactionID,
                            'name' : pipeline.name,
                            'description' : pipeline.description,
                           }
                active_list[pipeline.transactionID] = json_object
        result = json.dumps(active_list)
        
        return __count
    
    def get_pipeline(pipeline_id):
        global __active_ops
        pipeline = __active_ops.get(pipeline_id)
        result = None
        status_code = 0
        if pipeline is not None:
            result = {}
            result['id'] = pipeline.transactionID
            result['name'] = pipeline.name
            result['description'] = pipeline.description
            result = json.dumps(result)
            status_code = 200
        else:
            result = "Pipeline "+"'"+str(pipeline_id)+"' "+"does not exist."
            status_code = 404
        
        return result, status_code
    
    def register_model(data):
        key = data.get('Records')[0].get('s3').get('object').get('key')
        model_id = key.split('.')[0]
        if key is not None:
            try:
                client = Handler.__minio_connect__()
            except Exception as e:
                log.error('{0}'.format(str(e))) 
            if client is not None:
                response = client.get_object('models', key)
                content = response.data.decode('utf-8')
                model = Handler.__parse_file__(content)
                model._id = model_id
                ModelRegistry.register_model(model)
        else:
            log.error('Failed to retrieve MinIO key')
    
    def deregister_model(data):
        key = data.get('Records')[0].get('s3').get('object').get('key')
        if key is not None:
            model_id = key.split('.')[0]
            ModelRegistry.deregister_model(model_id)
    
    def __registry_init__():
        
        log.info('Initializing model registry...')
        ModelRegistry.init()
        client = Handler.__minio_connect__()
        if client is not None:
            try:
                found = client.bucket_exists("models")
                if not found:
                    log.info('MINIO ERROR: Bucket not found.')
                else:
                    files = client.list_objects('models')
                    for file in files:
                        if file.object_name.endswith('.config'):
                            model_id = file.object_name.split('.')[0]
                            response = client.get_object('models', file.object_name)
                            content = response.data.decode('utf-8')
                            model = Handler.__parse_file__(content)
                            model._id = model_id
                            ModelRegistry.register_model(model)
            except Exception as e:
                log.error('{0}'.format(str(e)))
            
        
    
    def __minio_connect__():
        
        client = None
        
        try:
            client = Minio(
                "isbpminio:9000",
                access_key="isbp",
                secret_key="isbpminio",
                secure=False
                )
        except Exception as e:
                client = None
                log.error('Failed to connect to MinIO: {0}'.format(str(e)))
        
        return client
    
    def __parse_file__(content):
        global __parser
        __parser.read_string(content)
        model_name = __parser['data']['name']
        model_metric = __parser['data']['metric']
        model_class = __parser['data']['class']
        model = Model(model_name, model_metric, model_class)
        return model
        
