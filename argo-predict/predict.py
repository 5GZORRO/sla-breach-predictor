# -*- coding: utf-8 -*-
"""
Created on Tue May 11 15:03:47 2021

@author: dlaskaratos
"""
import os
from os import path
from keras.models import load_model
import numpy as np
import json
from datetime import datetime
import requests

print('Loading model..')

model = load_model('/data/saved/lstm')
f = open('/data/data.json',)
data = json.load(f)
timestamp = data.get('timestamp')
x_input = data.get('data')
f.close()
X = np.array([x_input])
inp = X.reshape((X.shape[0], X.shape[1], 1))
yhat = model.predict(inp, verbose=0)
prediction = yhat[0][0]
operation_timestamp = datetime.now().strftime("%d-%m-%YT%H:%M")
os.remove('/data/data.json')
if not path.exists('/data/data.json'):
    print('File successfully removed')

data['value'] = str(prediction)
data['datetimeViolation'] = timestamp
data['datetimePrediction'] = operation_timestamp
del data['data']
del data['timestamp']

json = json.dumps(data)
r = requests.post('http://isbp:8000/service/set-prediction', data = json)
print(r.text)