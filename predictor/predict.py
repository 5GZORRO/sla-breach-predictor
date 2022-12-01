# -*- coding: utf-8 -*-
"""
Created on Tue May 11 15:03:47 2021

@author: dlaskaratos Intracom Telecom
"""

import json
from datetime import datetime
import requests
import logging

module = __import__('model')
models = {}

# def init_models():
#     logging.info('Initializing models...')
#     reg = {'lstmbw': 'LSTM', 'svrbw': 'SVR', 'nbeatsbw': 'NBeats'}
#     try:
#         for name, _class in reg.items():
#             Model = getattr(module, _class)
#             model = Model()
#             model.name = name
#             model.load('/data/models')
#             models[name] = model
#             logging.info('Model {0} loaded'.format(model.name))
#     except Exception as e:
#         logging.info(e)
        
def reload_model(_model: str, _class: str):
    logging.info('Reloading model {0} ...'.format(_model))
    result = None
    try:
        models[_model] = None
        Model = getattr(module, _class)
        model = Model()
        model.name = _model
        model.load('/data/models')
        models[_model] = model
        logging.info('Model {0} successfully reloaded'.format(model.name))
        result = 'Model ', model.name, 'successfully reloaded'
    except Exception as e:
        logging.info(e)
        result = 'Error reloading model ', model.name, ': ', str(e)
    return result
    

def get_predictions(data):
    name = data.get('name')
    transactionid = data.get('transactionID')
    logging.info('Received prediction requests for {0}:'.format(transactionid))
    timestamp = data.get('timestamp')
    x_input = data.get('data')
    model = models.get(transactionid.replace(":", "-")+"-"+name)
    prediction = float(model.predict(x_input))

    operation_timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    data['prediction'] = prediction
    data['datetimeViolation'] = timestamp
    data['datetimePrediction'] = operation_timestamp
    del data['data']
    del data['timestamp']
    data = json.dumps(data)
    r = requests.post('http://isbp:8000/service/set-prediction', data = data)
    print(r.text)
    
def copy_model(transactionid, path, name, _class):
        Model = getattr(module, _class)
        model = Model()
        model.name = name
        model.copy(path)
        model.load(path)
        models[transactionid+"-"+model.name] = model
        logging.info('Loaded model: {0}'.format(transactionid+", "+model.name))

def unload_model(transactionid, model):
    result = None
    transactionID = transactionid.replace(":", "-")+"-"+model
    del models[transactionID]
    if models.get(transactionID) is None:
        result = 'Model successfully unloaded.'
    else:
        result = 'Model not found or could not be unloaded.'
    return result

