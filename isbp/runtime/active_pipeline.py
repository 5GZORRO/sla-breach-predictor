# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 14:29:41 2020

@author: dlaskaratos ICOM
"""

from config.config import Config as cnf

class ActivePipeline():
    
    def __init__(self, transactionID, instanceID, productID, threshold, metric_name, operator, location) -> None:
        self.name = None
        self.description = None
        self.training_list = []
        self.prediction_list = []
        self.accuracies = []
        self.dates = []
        self.prediction_for_accuracy = 0
        self.points_for_median_accuracy = cnf.POINTS_FOR_MEDIAN_ACCURACY
        self.running_accuracy = 0
        self.median_accuracy = 0
        self.prediction_date = None
        self.features = 1
        self.n_steps = 3
        self.threshold = threshold
        self.metric = metric_name
        self.metricLink = 'http://www.provider.com/metrics/availability'
        self.transactionID = transactionID
        self.productID = productID
        self.instanceID = instanceID
        self.current_timestamp = None
        self.operator = operator
        self.location = location
        self.__waiting_on_ack = False
        self.model = 'lstm'
    
    @property
    def waiting_on_ack(self):
        return self.__waiting_on_ack
    
    @waiting_on_ack.setter
    def waiting_on_ack(self, value):
        self.__waiting_on_ack = value
    
    def get_single_prediction_accuracy(self, prediction_for_accuracy, real_value):
        accuracy = 0
        if real_value < prediction_for_accuracy:
            accuracy = real_value/prediction_for_accuracy
        else:
            accuracy = prediction_for_accuracy/real_value
                    
        return accuracy
    
    def check_violation(self, prediction):
        if self.operator == 'gt':
            if prediction > self.threshold:
                return True
            else:
                return False
        if self.operator == 'lt':
            if prediction < self.threshold:
               return True
            else:
               return False
        if self.operator == '.e':
            if prediction == self.threshold:
                return True
            else:
                return False