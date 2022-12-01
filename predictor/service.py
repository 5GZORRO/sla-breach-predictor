# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 09:42:03 2022

@author: dlaskaratos
"""

from fastapi import FastAPI, Response, Request, BackgroundTasks
import logging
from predict import reload_model, get_predictions, unload_model
from folder import create_transaction_folder, delete_transaction_folder

app = FastAPI()

@app.on_event('startup')
def on_startup():
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting ML forecast service...')
    # predict.init_models()
    

@app.post('/predict')
async def set_config(request:Request, background_tasks: BackgroundTasks):
    data = await request.json()
    background_tasks.add_task(get_predictions, data)
    return Response(content = 'Request received', media_type = 'text/plain')

@app.post('/load')
async def load_models(request:Request, background_tasks: BackgroundTasks):
    data = await request.json()
    background_tasks.add_task(create_transaction_folder, data)
    return Response(content = 'Request received', media_type = 'text/plain')

@app.post('/reload')
async def reload(request:Request):
    data = await request.json()
    model = data.get('model')
    _class = data.get('_class')
    result = reload_model(model, _class)
    return Response(content = result, media_type = 'text/plain')

@app.delete('/unload')
async def unload(request:Request):
    data = await request.json()
    transactionid = data.get('transactionid')
    model = data.get('model')
    result1 = delete_transaction_folder(transactionid)
    result2 = unload_model(transactionid, model)
    return Response(content = result1 + result2, media_type = 'text/plain')