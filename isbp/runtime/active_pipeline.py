# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 14:29:41 2020

@author: dlaskaratos ICOM
"""

from config.config import Config as cnf
import logging
from datetime import datetime
import statistics
from runtime.model_registry import ModelRegistry
import json
import requests
from enum import Enum

log = logging.getLogger(__name__)

class ActivePipeline():
    
    def __init__(self, transactionID, instanceID, productID, slaID, threshold, metric_name, operator, model, location, opaque_params, operation_type) -> None:
        self.name = None
        self.description = None
        self.training_list = []
        self.prediction_list = []
        self.accuracies = []
        self.dates = []
        self.prediction_for_accuracy = 0
        self.points_for_median_accuracy = cnf.POINTS_FOR_MEDIAN_ACCURACY
        self.running_accuracy = 0
        self.median_accuracy = 0.0
        self.prediction_date = None
        self.features = 1
        self.n_steps = 3
        self.threshold = threshold
        self.metric = metric_name
        self.metricLink = 'http://www.provider.com/metrics/availability'
        self.transactionID = transactionID
        self.productID = productID
        self.instanceID = instanceID
        self.slaID = slaID
        self.currentDate = None
        self.operator = operator
        self.location = location
        self.opaque_params = opaque_params
        self.operation_type = operation_type
        self.__waiting_on_ack = False
        self.model = model
        self.__status = Status.ACTIVE
        self.current_model = None
        self.isBlocked = False
        self.selection_accuracies = {}
        self.selection_predictions = {}
        self.historical_accuracy = {}
        self.historical_predictions = {}
        # self.__set_model_dicts__()
    
    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, value: int):
        self.__status = Status(value)
    
    @property
    def waiting_on_ack(self):
        return self.__waiting_on_ack
    
    @waiting_on_ack.setter
    def waiting_on_ack(self, value):
        self.__waiting_on_ack = value
    
    def get_single_prediction_accuracy(self, real_value):
            if real_value > 0.0:
                accuracy = 0
                if real_value < self.prediction_for_accuracy:
                    accuracy = real_value/self.prediction_for_accuracy
                else:
                    accuracy = self.prediction_for_accuracy/real_value
                if accuracy > 0.0:
                    log.info('--------{0}: Prediction Accuracy: {1}--------'.format(self.transactionID, str(accuracy)))
                self.accuracies.append(accuracy)
                        
    
    
    def calculate_median_accuracy(self):
        median_accuracy = 0.0
        if len(self.accuracies) == self.points_for_median_accuracy:
                model = self.current_model._id
                median_accuracy = statistics.mean(self.accuracies)
                log.info('--------{0}: Model {1} average accuracy is: {2}--------'.format(self.transactionID, model, median_accuracy))
                self.accuracies.clear()
        return median_accuracy
    
    def check_violation(self, prediction):
        if self.operator == '.g':
            return prediction > self.threshold
        elif self.operator == '.ge':
            return prediction >= self.threshold
        elif self.operator == '.l':
            return prediction < self.threshold
        elif self.operator == '.le':
            return prediction <= self.threshold
        elif self.operator == '.eq':
            return prediction == self.threshold
    
    # def set_model_prediction_for_accuracy(self, key, value):
    #     self.selection_predictions[key] = value
    #     self.historical_predictions.get(key).append(value)
    
    def try_insert(self, metric, date):
        
        if metric != 0 and self.currentDate != date:
            self.training_list.append(metric)
            self.prediction_list.append(metric)
            self.dates.append(date)
            self.currentDate = date
    
    def request_prediction(self, date):
        if len(self.prediction_list) == self.n_steps:
            if not self.isBlocked and not self.waiting_on_ack:
                log.info('Launching prediction job...')
                dictionary = {'transactionID': self.transactionID,
                          'instanceID' : self.instanceID,
                          'productID' : self.productID,
                          'timestamp' : date,
                          'data' : self.prediction_list,
                          'name': self.model.name,
                          'place' : self.location,
                          'opaque_params': self.opaque_params
                                          }
                data = json.dumps(dictionary)
                requests.post('http://predictor:8001/predict', data = data)
        
            self.prediction_list.pop(0)
        
    def check_training(self):
        if self.current_model != None and self.median_accuracy > 0.0 and self.median_accuracy < cnf.GLOBAL_ACCURACY:
            dictionary = {'model': self.current_model._id,
                          'class': self.current_model._class,
                          'pipeline': self.transactionID}
            with open(cnf.TEMP_FILE_PATH + self.transactionID+'-model.json', 'w') as outfile:
                json.dump(dictionary, outfile)
            log.info('Launching training job for {0} and model {1}'.format(self.transactionID, self.current_model._id))
            self.median_accuracy = 0.0
            self.clear_predictions()
            self.isBlocked = True
    
    def select_model(self):
        best_accuracy = 0
        model = None
        for key, value in self.selection_accuracies.items():
            average_accuracy = sum(value)/len(value)
            if average_accuracy > best_accuracy:
                best_accuracy = average_accuracy
                model = key
        
        last_model_prediction = self.selection_predictions.get(model)
        last_model_accuracies = self.selection_accuracies.get(model)
        self.accuracies = last_model_accuracies
        self.models = {}
        self.selection_accuracies = {}
        self.selection_predictions = {}
        model = ModelRegistry.get_model_by_name(model)
        if model is not None:
            self.current_model = model
            self.models[model._id] = model._class
            self.selection_predictions[model._id] = last_model_prediction
            self.selection_accuracies[model._id] = last_model_accuracies
            log.info('{0}: Selected model {1} with an average accuracy of {2}'.format(self.transactionID, model._id, str(best_accuracy)))
        else:
            log.error('Failed to select model')
        
    def clear_predictions(self):
        for key in self.selection_predictions.keys():
            self.selection_predictions[key] = 0

class Status(Enum):
    
    ACTIVE = 1
    TERMINATED = 2
    INACTIVE = 3