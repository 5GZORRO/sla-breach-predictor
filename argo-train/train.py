# -*- coding: utf-8 -*-
"""
Created on Wed May 19 11:26:09 2021

@author: dlaskaratos
"""

import os
from os import path
from keras.models import load_model
import pandas as pd
import numpy as np
import json
from zipfile import ZipFile

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


f = open('/data/metric.json',)
data = json.load(f)
metric = data.get('metric')
model = data.get('model')
f.close()

if not path.exists(model):
    from minio import Minio
    try:
            client = Minio(
                "isbpminio:9000",
                access_key="isbp",
                secret_key="isbpminio",
                secure=False
                )
            client.fget_object("models", model+'.zip', '/data/saved/'+model+'.zip')
            with ZipFile(model+'.zip', 'r') as _zip:
                _zip.extractall('/data/saved/'+model)
            print('Extraction complete')
            os.remove('/data/saved/'+model+'.zip')
    except Exception as e:
        client = None
        print('Failed to connect to MinIO: ' + str(e))

model = load_model('/data/saved/' + model)

print('Loading model..')
model = load_model('/data/saved/'+model)
data = pd.read_csv('/data/train.csv')
data = data['bw'].to_numpy().tolist()
X, y = split_sequence(data, 3)
X = X.reshape((X.shape[0], X.shape[1], 1))
model.fit(X, y, epochs=200, verbose=0)
print('Training completed')
os.remove('/data/train.csv')
if not path.exists('/data/train.csv'):
    print('File successfully removed')