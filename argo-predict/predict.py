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

model = load_model('/isbp-data/saved/lstm')
f = open('/isbp-data/data.json',)
data = json.load(f)
pipeline_id = data.get('pipeline_id')
timestamp = data.get('timestamp')
x_input = data.get('data')
f.close()
X = np.array([x_input])
inp = X.reshape((X.shape[0], X.shape[1], 1))
yhat = model.predict(inp, verbose=0)
prediction = yhat[0][0]
print('Prediction: ', str(prediction))
os.remove('/isbp-data/data.json')
if not path.exists('/isbp-data/data.json'):
    print('File successfully removed')

timestamp = str(timestamp)[:-5]
timestamp = int(timestamp)+60
timestamp = datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M")
d = {'pipeline_id' : pipeline_id, 'timestamp' : str(timestamp), 'prediction' : str(prediction)}
json = json.dumps(d)
r = requests.post('http://isbp:8000/service/set-prediction', data = json)
print(r.text)