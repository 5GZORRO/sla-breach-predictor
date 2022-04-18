# -*- coding: utf-8 -*-
"""
Created on Tue May 11 15:03:47 2021

@author: dlaskaratos Intracom Telecom
"""
import os
from os import path
import numpy as np
import json
from datetime import datetime
import requests
from zipfile import ZipFile


print('Loading model..')

f = open('/data/data.json','r')
data = json.load(f)
model_id = data.get('model_id')
lib = data.get('lib')
download = data.get('download')
timestamp = data.get('timestamp')
x_input = data.get('data')
f.close()
path_to_model = '/data/saved/'+model_id
zip_model = path_to_model + '/' + model_id+'.zip'

if not path.exists(path_to_model):
    os.mkdir(path_to_model)

if download:
    from minio import Minio
    try:
            client = Minio(
                "isbpminio:9000",
                access_key="isbp",
                secret_key="isbpminio",
                secure=False
                )
            client.fget_object("models", model_id+'.zip', zip_model)
            with ZipFile(zip_model, 'r') as _zip:
                _zip.extractall(path_to_model)
            print('Extraction complete')
            os.remove(zip_model)
    except Exception as e:
        client = None
        print('Error: ', e)


if lib == 'keras':
    from keras.models import load_model
    model = load_model(path_to_model)
    X = np.array([x_input])
    inp = X.reshape((X.shape[0], X.shape[1], 1))
    yhat = model.predict(inp, verbose=0)
    prediction = yhat[0][0]
elif lib == 'sklearn':
    from sklearn.svm import SVR
    from joblib import load
    model = load(path_to_model+'/'+model_id+'.joblib')
    X = np.array([x_input])
    inp = X = X.reshape((X.shape[0], X.shape[1]))
    yhat = model.predict(inp)
    prediction= yhat[0]

operation_timestamp = datetime.now().strftime("%d-%m-%YT%H:%M")
print('Prediction at '+ datetime.now().strftime("%d-%m-%YT%H:%M")+': '+ str(prediction))
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