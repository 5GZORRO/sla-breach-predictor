# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 11:41:00 2021

@author: dlaskaratos ICOM

Handles the delegation of the requests from the REST Controller by 
constructing an ActivePipeline or modifiying an existing one.

- __active_ops: dictionary containing active pipelines with the execution id as the key

"""

from runtime.active_pipeline import ActivePipeline, Status
from config.config import Config as cnf
from runtime.http_connectors import register_pipeline, get_sla_details, load_models, delete_transaction_folder
from runtime.model_registry import Model, ModelRegistry
from minio import Minio
from minio.error import S3Error
import json
import os
import logging
from zipfile import ZipFile
from configparser import ConfigParser
import requests

log = logging.getLogger(__name__)


class Handler():
    
    __active_ops = None
    __parser = None
    __count = 0
    __p_counter = 0
    
    def init():
        global __active_ops
        global __count
        global __parser
        global __p_counter
         
        __active_ops = {}
        __count = 0
        __p_counter = 0
        __parser = ConfigParser()
        Handler.__upload_models()
        Handler.__registry_init__()
    
    def get_list():
        global __active_ops
        return __active_ops
    
    def create_new_pipeline(data):
        global __active_ops
        global __count
        # log.info(data)
        transactionID = data.get('transactionID')
        productID = data.get('productID')
        instanceID = data.get('instanceID')
        slaID = data.get('SLAID')
        location = data.get('place')
        opaque_params = data.get('opaque_params')
        operation_type = data.get('consequence')
        pipeline = __active_ops.get(transactionID)
        if pipeline is not None:
            log.info('Pipeline already exists')
            status = 'Pipeline already exists'
        else:
            try:
                sla_details, status = get_sla_details(slaID)
                log.info(status)
                if sla_details is not None:
                    rule = sla_details.get('rule')[0]
                    threshold = float(rule.get('referenceValue'))
                    operator = rule.get('operator')
                    metric_name = rule.get('metric')
                    model = ModelRegistry.get_model_by_name('lstmbw')
                    pipeline = ActivePipeline(transactionID, 
                                              instanceID, 
                                              productID, 
                                              slaID, 
                                              threshold, 
                                              metric_name, 
                                              operator, 
                                              model, 
                                              location, 
                                              opaque_params, 
                                              operation_type)
                    __active_ops[pipeline.transactionID] = pipeline
                    pipeline.threshold = 22.0
                    __count = __count + 1
                    log.info('Created new pipeline with transactionID: {0} and models: {1}'.format(pipeline.transactionID, pipeline.model.name))
                    register_pipeline(pipeline.productID)
                    load_models(pipeline.transactionID, model.name, model._class)
                else:
                    log.info('SLA with transactionID {0} and SLAID {1} could not be retrieved'.format(transactionID, slaID))    
            except Exception as e:
                log.info('Error: {0}'.format(e))
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
            delete_transaction_folder(pipeline.transactionID, pipeline.model.name)
            result = 'Pipeline successfully terminated.'
            status_code = 200
        
        return result, status_code
        
    def set_prediction(data):
        global __active_ops
        global __p_counter
        
        __p_counter = __p_counter+1
        result = None
        pipeline_id = data.get('transactionID')
        prediction = data.get('prediction')
        timestamp = data.get('datetimeViolation')
        pipeline = Handler.get_active_pipeline(pipeline_id)
        if pipeline is not None:
            if not pipeline.isBlocked:
                pipeline.prediction_for_accuracy = prediction
                if __p_counter%5==0 or __p_counter%5==5:
                    log.info('{0}: Received prediction with value {1}'.format(pipeline_id, str(prediction)))
                result = 'Prediction set successfully'
        else:
            result = 'Pipeline not found.'
            
        return result, pipeline, prediction
                
    
    def get_active_list():
        global __active_ops
        global __count
        result = None

        # Initialize an empty list
        active_list = []
        
        if __count < 1:
            result = 'No active pipelines.'
        else:
            for (key, value) in __active_ops.items():
                if value.status == Status.Active:
                    json_object = {'transactionID' : value.transactionID,
                            'productID' : value.productID,
                            'instanceID' : value.instanceID,
                            'metric': value.metric,
                            'threshold': value.threshold,
                            'operator': value.operator,
                            'location': value.location,
                            'model': value.model
                            }
                    active_list.append(json_object)
        result = json.dumps(active_list)
        
        return result, __count
    
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
    
    def get_metrics(pipeline_id):
        global __active_ops
        response = None
        code = 0
        mdl = {}
        isSelected = False
        pipeline = __active_ops.get(pipeline_id)
        if pipeline is not None:
            for model, _class in ModelRegistry.get_all_models_by_name().items():
                dic = {}
                accuracies = pipeline.historical_accuracy.get(model)
                predictions = pipeline.historical_predictions.get(model)
                current_accuracy = accuracies[-1] if len(accuracies) != 0 else None
                current_error = 1 - current_accuracy if current_accuracy is not None else None
                prediction = predictions[-1] if len(predictions) != 0 else None
                dic['current_accuracy'] = current_accuracy
                dic['current_error'] = current_error
                dic['prediction'] = prediction
                if model == pipeline.current_model:
                    isSelected = True
                dic['isSelected'] = isSelected
                mdl[_class] = dic
            response = {'models': mdl}
            code = 200
        else:
            response = 'ERROR: Pipeline not found.'
            code = 404
        response = json.dumps(response)
        return response, code
    
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
    
    def reload_model(data):
        data = json.dumps(data)
        requests.post('http://predictor:8001/reload', data = data)
    
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
                        else:
                            client.fget_object("models", file.object_name, '/data/models/'+file.object_name)
                            with ZipFile('/data/models/'+file.object_name, 'r') as _zip:
                                _zip.extractall('/data/models/')
                            log.info('Extraction of {0} complete'.format(file.object_name))
                            os.remove('/data/models/'+file.object_name)
            except Exception as e:
                log.error('{0}'.format(e))
            
        
    
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
                log.error('Failed to connect to MinIO: {0}'.format(e))
        
        return client
    
    def __parse_file__(content):
        global __parser
        __parser.read_string(content)
        model_name = __parser['data']['name']
        model_metric = __parser['data']['metric']
        model_class = __parser['data']['class']
        model_lib = __parser['data']['lib']
        model = Model(model_name, model_metric, model_class, model_lib)
        return model
        
    def __upload_models():
        from minio import Minio
        log.info('Uploading models...')
        try:
                client = Minio(
                "isbpminio:9000",
                access_key="isbp",
                secret_key="isbpminio",
                secure=False
                )
                for filename in os.listdir('models/'):
                    result = client.fput_object("models", filename, 'models/'+filename)
        except Exception as e:
                print(e)
