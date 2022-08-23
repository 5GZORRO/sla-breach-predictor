# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 09:42:03 2022

@author: dlaskaratos
"""

from fastapi import FastAPI, Response, Request, BackgroundTasks
import logging
import predict

app = FastAPI()

@app.on_event('startup')
def on_startup():
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting ML forecast service...')
    predict.init_models()
    

@app.post('/predict')
async def set_config(request:Request, background_tasks: BackgroundTasks):
    data = await request.json()
    background_tasks.add_task(predict.get_predictions, data)
    return Response(content = 'Request received', media_type = 'text/plain')

@app.post('/reload')
async def reload(request:Request):
    data = await request.json()
    model = data.get('model')
    _class = data.get('_class')
    result = predict.reload_model(model, _class)
    return Response(content = result, media_type = 'text/plain')