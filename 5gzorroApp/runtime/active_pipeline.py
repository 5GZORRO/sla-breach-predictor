# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 14:29:41 2020

@author: dlaskaratos ICOM
"""

from algorithms.model_manager import ModelManager as manager
from messaging.kclients import Consumer, Producer
import logging
from config.config import Config as cnf
import time
import json
from exceptions.exceptions import MetricNotFoundException
from datetime import datetime
import pandas as pd

log = logging.getLogger(__name__)

class ActivePipeline():
    
    def __init__(self, _id, name, description, rules) -> None:
        self.id = int(_id)
        self.name = name
        self.description = description
        self.models = self.__extract_rules__(self.id, rules)
        # self.train_consumer = None
        # self.predict_consumer = None
        self.offset = 0
        
    
    def start_training(self, model_entity):
        consumer = Consumer()
        consumer.subscribe(cnf.MON_TOPIC)
        model_entity.active_training = True
        data_points = cnf.TRAIN_DATA_POINTS
        dataset = list()
        
        while(model_entity.active_training):
            
                 for message in consumer.consumer:
                     dct = message.value.decode('utf-8')
                     data = json.loads(dct)
                     metric = data[model_entity.metric]
                     dataset.append(float(metric))
                     # model_entity.value_list.append([int(str(data['time'])[:-5]), metric])
                     if len(dataset) >= data_points:
                     # try: 
                        self.offset = message.offset
                        model_entity.train(dataset[0:data_points])
                        manager.save_model(self.id, model_entity)
                        model_entity.new_model = True
                        model_entity.model_available = True
                        dataset = dataset[data_points:]
                        log.info('Model successfully saved')
                        time.sleep(cnf.TR_TMT)
                     # except Exception as ex:
                     #    result = "Error during model training or saving: " + str(ex)
                     #    log.error(result)
                     
                     
        
    def start_predicting(self, model_entity):
        consumer = Consumer()
        consumer.subscribe(cnf.MON_TOPIC)
        counter = 0
        model_entity.active_prediction = True
        prediction_for_accuracy = 0
        
        while(not model_entity.model_available):
            counter += 1
            log.info('WAITING FOR A MODEL TO BE AVAILABLE... %s', counter)
            time.sleep(cnf.W_TMT)
        
        log.info('STARTING PREDICTION CYCLE')
        
        metrics = list()
        dates = list()
        
        while(model_entity.active_prediction):
            
            consumer.consumer.seek(consumer.partition, self.offset)
            
            try:
                for message in consumer.consumer:
                    dct = message.value.decode('utf-8')
                    data = json.loads(dct)
                    dates.append(data['time'])
                    metric = data[model_entity.metric]
                    if metric is not None:
                        metrics.append(float(metric))
                        if prediction_for_accuracy != 0:
                            single_accuracy = self.get_single_prediction_accuracy(prediction_for_accuracy, float(metric))
                            model_entity.accuracy += single_accuracy
                            model_entity.prediction_counter += 1
                    else:
                        raise MetricNotFoundException(model_entity.metric)
                        # result_array = data.get('data').get('result')
                        # for item in result_array:
                        #     metric = item.get('metric')
                        #     if metric is not None:
                        #         name = metric.get('__name__')
                        #         if name != model_entity.metric:
                        #             continue
                        #         else:
                        #             value = item.get('value')
                        #             dates.append(value[0]) # timestamp
                        #             metrics.append(float(value[1])) # metric value
                        #     else:
                        #         raise MetricNotFoundException(model_entity.metric)
                    if len(metrics) == model_entity.n_steps:
                        
                        if model_entity.new_model: 
                            load_result, saved_model = manager.load_model(self.id, model_entity.get_id())
                            if saved_model != None:
                                model_entity.set_model(saved_model)
                                model_entity.new_model = False
                            else:
                                log.error("Could not load new model. %s", load_result)
                        
                        prediction = model_entity.predict(metrics)
                        prediction_for_accuracy = prediction
                        timestamp = str(dates[len(dates)-1])[:-5]
                        entry = [int(timestamp), prediction]
                        model_entity.prediction_list.append(entry)
                        timestamp = int(timestamp)+60
                        date = datetime.fromtimestamp(timestamp)
                        metrics.pop(0)
                        if prediction > model_entity.threshold:
                            notification = 'Predicted violation of threshold '+str(model_entity.threshold)+' with value: '+str(prediction)+ ' at '+str(date)
                            Producer.send(notification)

            except Exception as e:
                log.error('Error during prediction process: %s', str(e))

        
    def update_model(self, model_data):
        log.info('Terminating current running operations...')
        try:
            self.terminate_operations(clean_up = False)
            log.info('Constructing new model...')
            self.__model_entity = manager.construct_model_entity(model_data)
            result = 'Model successfully updated.'
            log.info(result)
        except Exception as e:
            result = 'Failed to update model: ', str(e)
        
        return result
                
           
    def write_values_to_log(self, entity, _list, _round):
        logs_path = cnf.LOGS
        try:
            file = open(logs_path+entity.get_id()+str(_round)+".log", "a+")
            for line in _list:
                file.write(str(line)+"\n")
        except Exception as ex:
            logging.error(str(ex))
        
    def __extract_rules__(self, pipeline_id, rules):
        models = {}
        for rule in rules:
            model_entity = manager.construct_model_entity(pipeline_id, rule)
            models[model_entity.id] = model_entity
        return models
    
    def get_single_prediction_accuracy(self, prediction_for_accuracy, real_value):
        accuracy = 0
        if real_value > prediction_for_accuracy:
            accuracy = prediction_for_accuracy/real_value
        else:
            accuracy = real_value/prediction_for_accuracy
                    
        return accuracy
        
    
    def calculate_accuracy(self, model_entity):
        
        accuracy = None
        count = 0
        value_list = model_entity.value_list.copy()
        prediction_list = model_entity.prediction_list.copy()
        
        if len(value_list) == 0 or len(prediction_list) == 0:
            return 0
        
        for value_pair in value_list:
            for pred_pair in prediction_list:
                if value_pair[0] == pred_pair[0]:
                    count += 1
                    value = value_pair[1]
                    prediction = pred_pair[1]
                    
                    if value > prediction:
                        acc = prediction/value
                    else:
                        acc = value/prediction
                    
                    accuracy += acc
                    break
        
        return accuracy/count
                    
                    
        
        
        
        
        




