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
from runtime.http_connectors import register_app
import logging
import threading
from os import path
import shutil
import ctypes
import json

app = FastAPI()
consumer = None
consumer_thread = None

@app.on_event('startup')
def on_startup():
    logging.basicConfig(level=logging.INFO)
    global consumer
    global consumer_thread
    global topic_list
    copy_model()
    Config.load_configuration()
    Handler.init()
    register_app()
    producer_result = Producer.init()
    logging.info(producer_result)
    consumer_result, consumer = Consumer.init()
    logging.info(consumer_result)
    if consumer is not None:
        Consumer.subscribe(Config.TOPICS)
        consumer_thread = threading.Thread(target = Consumer.start)
        consumer_thread.start()
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
    write_to_file()
    return HTMLResponse(content = index, status_code = 200)


def write_to_file():
    dictionary = {'pipeline_id' : 123, 'timestamp' : 1589676626361.0, 'data' : [1954.0929, 1954.0929, 1976.6895]}
    with open('/data/data.json', 'w') as outfile:
        json.dump(dictionary, outfile)

@app.post('/add-topic/{topic_name}')
def set_new_topic(topic_name: str):
    global consumer
    global topic_list
    topic_list.append(topic_name)
    consumer.subscribe(topic_list)
    return Response('Topic received')

@app.post('/service/sla')
async def submit_slaID(request: Request):
    data = await request.json()
    pipeline, status = Handler.create_new_pipeline(data)
    return Response(content = status, media_type = Media.TEXT_PLAIN)

def copy_model():
    src = 'save/'
    dest = '/data/saved/'
    
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
        if pipeline.check_violation(prediction):
            notification = breach_notification(data, prediction)
            Producer.send(notification)
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

def breach_notification(data, prediction):
    data['value'] = prediction
    data = {'breachPredictionNotification' : data}
    data = json.dumps(data)
    return data


class Media():
    APP_JSON = 'application/json'
    APP_XML = 'application/xml'
    TEXT_PLAIN = 'text/plain'


