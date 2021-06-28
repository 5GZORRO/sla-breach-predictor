# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 15:29:57 2020

@author: dlaskaratos ICOM
"""

from fastapi import FastAPI, Response, Request, BackgroundTasks
from messaging.kafka_clients import Consumer, Producer
from fastapi.responses import HTMLResponse
from runtime.handler import Handler
from config.config import Config
from http_connector import poll
import logging
import threading
from os import path
import shutil
import ctypes
import json
import pandas as pd

app = FastAPI()
consumer = None
consumer_thread = None
poll_thread = None
topic_list = ['isbp-topic']
data_counter = 0

@app.on_event('startup')
def on_startup():
    logging.basicConfig(level=logging.INFO)
    global consumer
    global consumer_thread
    global topic_list
    global poll_thread
    Config.load_configuration()
    Handler.init()
    Handler.init_scaler()
    producer_result = Producer.init()
    logging.info(producer_result)
    consumer_result, consumer = Consumer.init()
    logging.info(consumer_result)
    poll_thread = threading.Thread(target = poll)
    poll_thread.start()
    if consumer is not None:
        Consumer.subscribe(topic_list)
        consumer_thread = threading.Thread(target = Consumer.start)
        consumer_thread.start()
    # copy_model()
    logging.info('Starting ISBP service...')


@app.on_event('shutdown')
def on_shutdown():
    global consumer_thread
    global poll_thread
    logging.info('Shutting down consumer...')
    result = Consumer.stop()
    logging.info(result)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(consumer_thread.ident,  ctypes.py_object(SystemExit))
    if res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(consumer_thread.ident, 0)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(poll_thread.ident,  ctypes.py_object(SystemExit))
    if res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(poll_thread.ident, 0)

@app.get('/')
def read_root():
    index = """
         <!DOCTYPE html>
         <html>
<head>
  <meta name="keywords" content="HTML,CSS,XML,JavaScript">
</head>
<body>

<h1>Please provide request parameters.</h1>

<form action="">
  <label for="steps">Steps:</label>
  <input type="text" id="steps" name="steps"><br><br>
  <label for="features">Features:</label>
  <input type="text" id="features" name="features"><br><br>
  <button type="buton" onclick="send()"> Send </button>
</form>
</body>
</html>
         """
    # write_to_file()
    return HTMLResponse(content = index, status_code = 200)

def write_to_file():
    dictionary = {'pipeline_id' : 123, 'timestamp' : 1589676626361.0, 'data' : [1954.0929, 1954.0929, 1976.6895]}
    with open('/isbp-data/data.json', 'w') as outfile:
        json.dump(dictionary, outfile)

@app.post('/add-topic/{topic_name}')
def set_new_topic(topic_name: str):
    global consumer
    global topic_list
    topic_list.append(topic_name)
    consumer.subscribe(topic_list)
    return Response('Topic received')

def copy_model():
    src = 'save/'
    dest = '/isbp-data/saved/'
    
    if not path.exists(dest):
        shutil.copytree(src, dest) 


@app.post('/service/start')
async def start_pipeline(request: Request):
    data = await request.json()
    result, code = Handler.create_new_pipeline(data)
    return Response(status_code = code, content = result, media_type = Media.TEXT_PLAIN)

@app.delete('/service/pipeline/stop/{pipeline_id}')
def stop_pipeline(pipeline_id: str, request: Request):
    result, code = Handler.terminate_pipeline(pipeline_id)
    return Response(status_code = code, content = result, media_type = Media.TEXT_PLAIN)

@app.post('/service/set-prediction')
async def set_prediction(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    result, pipeline, prediction = Handler.set_prediction(data)
    if pipeline is not None:
        if prediction < pipeline.threshold:
            data['value'] = prediction
            data = {'breachPredictionNotification' : data}
            data = json.dumps(data)
            Producer.send(data)
    return Response(result, media_type = Media.TEXT_PLAIN)

@app.get('/service/pipeline/{pipeline_id}')
def get_pipeline(pipeline_id: str):
    result, code = Handler.get_pipeline(pipeline_id)
    return Response(status_code = code, content = result, media_type = Media.APP_JSON)

@app.get('/get-active-list')
def get_active_predictions():
    result = Handler.get_active_list()
    return Response(str(result))

@app.post('/service/reconnect')
def force_reconnect():
    consumer_result, consumer = Consumer.init()
    producer_result = Producer.init()
    return Response(consumer_result+'\n'+producer_result, media_type = Media.TEXT_PLAIN)

@app.get('/monitoringData')
def get_monitoring_data():
    global data_counter
    value = None
    timestamp = None
    j = {"status": "success",
         "data": {
             "resultType": "matrix",
             "result": [
             {
                "metric": {
                    "__name__": "availability",
                    "job": "prometheus",
                    "instance": "http://5gzorro_osm.com"
                },
                "values": [
                    [
                        
                    ]
                ]
            }
        ]
    }
}
    
    data = pd.read_csv('dataset.csv')
    if data_counter + 1 > len(data)-1:
        data_counter  = 0
    item = data[data_counter : data_counter +1]
    for index, row in item.iterrows():
        value = row['availability-percent']
        timestamp = row['unix-timestamp']
    
    l = [[timestamp, value]]
    j['data']['result'][0]['values'] = l

    data = json.dumps(j)
    data_counter = data_counter + 1
    return Response(data, media_type = Media.APP_JSON)


class Media():
    APP_JSON = 'application/json'
    APP_XML = 'application/xml'
    TEXT_PLAIN = 'text/plain'


