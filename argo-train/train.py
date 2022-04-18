# -*- coding: utf-8 -*-
"""
Created on Wed May 19 11:26:09 2021

@author: dlaskaratos Intracom Telecom
"""

import os
from os import path
from os.path import basename
import pandas as pd
import numpy as np
import json
from zipfile import ZipFile
import requests

def split_sequence(sequence, n_steps):
        
        X, y = list(), list()
        for i in range(len(sequence)):
            end_ix = i + n_steps
            if end_ix > len(sequence)-1:
                break
            seq_x, seq_y = sequence[i:end_ix], sequence[end_ix:end_ix+1]
            X.append(seq_x)
            y.append(seq_y)
        return np.array(X), np.array(y)

def upload_model(client, filename, path):
    if client is None:
        from minio import Minio
        client = Minio(
                "isbpminio:9000",
                access_key="isbp",
                secret_key="isbpminio",
                secure=False
                )
    
    result = client.fput_object("models", filename, path,)
    os.remove(path)
    print (result.object_name)

f = open('../data/model.json',)
data = json.load(f)
lib = data.get('lib')
model_id = data.get('model_id')
f.close()
path_to_model = '../data/saved/'+model_id
zip_model = path_to_model+'/'+model_id+'.zip'
data = pd.read_csv('../data/train.csv')
data = data['bw'].to_numpy().tolist()
X, y = split_sequence(data, 3)

print('Loading model..')

client = None
success = None

if not path.exists(path_to_model):
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
        print('Failed to connect to MinIO: ', e)

try:
    if lib == 'keras':
        from keras.models import load_model
        model = load_model(path_to_model)
        X = X.reshape((X.shape[0], X.shape[1], 1))
        model.fit(X, y, epochs=200, verbose=0)
        model.save(path_to_model)
        with ZipFile(zip_model, 'w') as zipObj:
        # Iterate over all the files in directory
            for folderName, subfolders, filenames in os.walk(path_to_model):
                for filename in filenames:
                    #create complete filepath of file in directory
                   filePath = os.path.join(folderName, filename)
                   # Add file to zip
                   zipObj.write(filePath, basename(filePath))
        success = True
    elif lib == 'sklearn':
        from sklearn.svm import SVR
        from joblib import dump, load
        model = load(path_to_model+'/'+model_id+'.joblib')
        X = X.reshape((X.shape[0], X.shape[1]))
        model.fit(X, y)
        dump(model, path_to_model+'/'+model_id+'.joblib')
        with ZipFile(zip_model, 'w') as zipObj:
            zipObj.write(path_to_model+'/'+model_id+'.joblib')
        success = True
except Exception as e:
    print('Exception: ', e)
    success = False

os.remove('/data/train.csv')
os.remove('/data/metric.json')
if not path.exists('/data/train.csv'):
    print('File successfully removed')
if not path.exists('/data/metric.json'):
    print('File successfully removed')

if success:
    print('\nTraining completed')
    data = {"id": model_id}
    data = json.dumps(data)
    upload_model(client, model_id+'.zip', zip_model)
    request = requests.post('http://isbp:8000/service/donwload-model', data = data)