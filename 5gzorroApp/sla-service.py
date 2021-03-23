# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 15:29:57 2020

@author: dlaskaratos ICOM
"""

from fastapi import FastAPI, Request, Response, BackgroundTasks
from fastapi.responses import HTMLResponse
import logging
from algorithms.model_manager import ModelManager
from algorithms.model_descriptor import ModelDescriptor
from runtime.handler import Handler, ClientData
from runtime.operation_manager import OperationManager
from messaging.kclients import Producer
from config.config import Config

app = FastAPI()

@app.on_event('startup')
def on_startup():
    logging.basicConfig(level=logging.INFO)
    logging.info("Loading configuration...")
    Config.load_configuration()
    Producer.init()
    Handler.init()
    ModelManager.init()
    ModelDescriptor.init()
    OperationManager.init()
    logging.info("Starting web service...")


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

<script>
function send() {
  var steps = document.getElementById("steps").value;
  var features = document.getElementById("features").value;
  var request = new XMLHttpRequest();
    request.open("GET", "http://127.0.0.1:8000/service/?params=n_steps:" + steps + ",n_features:" + features, true);
    request.send(null);
	request.onreadystatechange = function() {
        if (request.readyState === 4 && request.status === 200) {
            alert(request.responseText);
        }
        request.onerror = function (e) {
            alert("error: " +request.status);
        };
    };
}
</script>

</body>
</html>
         """
    return HTMLResponse(content = index, status_code=200)

@app.post('/service/prediction/terminate')
def stop_prediction_cycle(params: ClientData):
    pipeline = Handler.get_active_pipeline(params.unique_id)
    result = None
    if pipeline == None:
        result = "Operation "+"'"+params.unique_id+"' "+"does not exist."
    elif not pipeline.models.get(params.model_id).active_prediction:
        result = 'Prediction is already inactive for this operation.'
    else:
        pipeline.models.get(params.model_id).active_prediction = False
        result = 'Stopping prediction...'
   
    return Response(result, media_type = Media.TEXT_PLAIN)

@app.post('/service/training/terminate')
def stop_training_cycle(params: ClientData):
    pipeline = Handler.get_active_pipeline(params.id)
    result = None
    if pipeline == None:
        result = "Operation "+"'"+params.id+"' "+"does not exist."
    elif not pipeline.models.get(params.model_id).active_training:
        result = 'Training is already inactive for this operation.'
    else:
        pipeline.models.get(params.model_id).active_training = False
        result = 'Stopping training...'
   
    return Response(result, media_type = Media.TEXT_PLAIN)

@app.post('/service/terminate')
async def terminate_pipeline(request: Request):
    data = await request.json()
    pipeline = Handler.get_active_pipeline(data['id'])
    result = None
    if pipeline == None:
        result = "Operation "+"'"+pipeline.id+"' "+"does not exist."
    else:
        result = Handler.terminate(pipeline.id)
    
    return Response(result, media_type = Media.TEXT_PLAIN)
    

@app.post('/service/start')
async def start_pipeline(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    pipeline = Handler.create_new_pipeline(data)
    result = Handler.start_pipeline(pipeline)
    return Response(result, media_type = Media.TEXT_PLAIN)

@app.get('/service/get_pipeline/{pipeline_id}')
def get_pipeline(pipeline_id: int):
    result = Handler.get_pipeline(pipeline_id)
    return Response(result, media_type = Media.APP_JSON)

@app.post('/service/update')
async def update_pipeline(request: Request):
    data = await request.json()
    result = Handler.update_pipeline(data)    
    return Response(result, media_type = Media.TEXT_PLAIN)

@app.post('/configure')
def configure_algorithm(params: ClientData, background_tasks: BackgroundTasks):
    pipeline = Handler.get_active_pipeline(params.unique_id)
    if pipeline != None:
        result = 'Configuring algorithm... Starting new training'
        background_tasks.add_task(Handler.configure_algorithm, params)
    else:
        result = "Operation "+"'"+params.unique_id+"' "+"does not exist."
    
    return Response(result, media_type = Media.TEXT_PLAIN)

@app.get('/get-active-list')
def get_active_predictions():
    active_list = Handler.get_active_list()
    # count = OperationManager.get_global_active_count()
    return Response(active_list, media_type = Media.APP_JSON)


############################### ONLY FOR TESTING PURPOSES ###########################

@app.post('/service/train')
def train(params: ClientData, background_tasks: BackgroundTasks):
    pipeline = Handler.create_new_pipeline(params)
    pipeline.set_active_training(True)
    background_tasks.add_task(pipeline.start_training)
    return Response('Training started...', media_type = Media.TEXT_PLAIN)

@app.post('/service/predict')
def predict(params: ClientData, background_tasks: BackgroundTasks):
    pipeline = Handler.get_or_create(params)
    
    background_tasks.add_task(pipeline.predict)
    return Response('Prediction started...', media_type = Media.TEXT_PLAIN)

#####################################################################################


class Media():
    APP_JSON = 'application/json'
    APP_XML = 'application/xml'
    TEXT_PLAIN = 'text/plain'
    