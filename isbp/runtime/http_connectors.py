# Helper methods that perform HTTP requests to 5GZORRO modules to retrieve or post information

from config.config import Config as cnf
import requests
import json
import logging

params = {'userId' : 'isbp', 'authToken' : 'blah'}

def register_app():

    global params
    register_url = 'http://172.28.3.94:8080/datalake/v1/user'
    
    request = requests.post(register_url, json = params)
    if request.status_code == 409:
        logging.info('App already registered.Getting information.')
        request = requests.get(register_url, json = params)
        
    response = json.loads(request.text)
    data_topic = response.get('availableResources').get('topics').get('userInTopic')
    kafka_url = response.get('availableResources').get('urls').get('kafka_url').split(':')
    cnf.TOPICS.append(data_topic)
    cnf.KAFKA_HOST = kafka_url[0]
    cnf.KAFKA_PORT = kafka_url[1]
    cnf.MON_DATA_TOPIC = data_topic
    

def register_pipeline(slaID):
    global params
    register_url = 'http://172.28.3.46:30887/datalake/v1/stream_data/register/'+slaID
    
    token = {'userInfo' : params, 'productInfo' : {'topic' : cnf.MON_DATA_TOPIC}}
    request = requests.post(register_url, json = token)
    if request.status_code > 200 and request.status_code < 300:
        logging.info("Successfully registered pipeline with ID: {0}".format(slaID))
    else:
        logging.info("Registration failed.")
        
    

def get_sla_details(slaID):
    sla_url = 'http://172.28.3.6:31080/smart-contract-lifecycle-manager/api/v1/service-level-agreement/'
    response = None
    request = requests.get(sla_url+slaID)
    logging.info('SLA status: {0}'.format(request.status_code))
    if request.status_code == 200:
        response = json.loads(request.text)
        result = 'SLA details successfully retrieved'
    else:
        result = 'SLA not found or could not be retrieved'
    
    return response, result