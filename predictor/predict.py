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

def init_models():
    logging.info('Models initialized')
    reg = {'lstmbw': 'LSTM', 'svrbw': 'SVR', 'nbeatsbw': 'NBeats'}
    for name, _class in reg.items():
        Model = getattr(module, _class)
        model = Model()
        model.name = name
        model.load('/data/models')
        models[name] = model
    

def get_predictions(data):
    # name = data.get('name')
    # _class = data.get('class')
    logging.info('Received prediction requests for {0}:'.format(data.get('transactionID')))
    timestamp = data.get('timestamp')
    model_list = data.get('models')
    x_input = data.get('data')
    predictions = {}
    for name, _class in model_list.items():
        model = models.get(name)
        model.load('/data/models')
        prediction = model.predict(x_input)
        predictions[name] = float(prediction)
    
    operation_timestamp = datetime.now().strftime("%d-%m-%YT%H:%M")
    data['predictions'] = predictions
    data['datetimeViolation'] = timestamp
    data['datetimePrediction'] = operation_timestamp
    del data['data']
    del data['timestamp']
    data = json.dumps(data)
    r = requests.post('http://qmp:8000/service/set-prediction', data = data)
    print(r.text)

