# -*- coding: utf-8 -*-
"""
Created on Wed May 19 11:26:09 2021

@author: dlaskaratos Intracom Telecom
"""

import os
from os import path
import pandas as pd
import json
import requests
import argparse

def upload_model(filename, path):
    from minio import Minio
    try:
        client = Minio(
                "qmpminio:9000",
                access_key="isbp",
                secret_key="isbpminio",
                secure=False
                )
    
        result = client.fput_object("models", filename, path,)
        os.remove(path)
        print ('Object ', result.object_name, 'successfully stored')
    except Exception as e:
        print(e)


parser = argparse.ArgumentParser(description='Provide parameters for the Predict module.')
parser.add_argument('filename', type=str)
args = parser.parse_args()
filename = args.filename

base_path = '../data/'
f = open(filename,)
data = json.load(f)
_class = data.get('class')
name = data.get('model')
pipeline = data.get('pipeline')
f.close()
data = pd.read_csv(base_path+'dataset.csv')
data = data['bw'].to_numpy().tolist()
module = __import__('model')
print('Loading model..')

Model = getattr(module, _class)
model = Model()
model.name = name
model.load()
success, path_to_model = model.train(data)

print('Success :', success)

# os.remove(base_path+'/train.csv')
os.remove(filename)
# if not path.exists(base_path+'/train.csv'):
#     print('File successfully removed')
if not path.exists(filename):
    print('File successfully removed')
    

if success:
    print('\nTraining completed')
    data = {"name": model.name,
            'pipeline': pipeline}
    data = json.dumps(data)
    #upload_model(model.name, path_to_model)
    # os.remove(path_to_model)
    request = requests.post('http://qmp:8000/service/donwload-model', data = data)