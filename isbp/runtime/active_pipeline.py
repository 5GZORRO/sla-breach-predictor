# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 14:29:41 2020

@author: dlaskaratos ICOM
"""

from config.config import Config as cnf

class ActivePipeline():
    
    def __init__(self, _id, name, description, features, n_steps, threshold) -> None:
        self.id = _id
        self.name = name
        self.description = description
        self.training_list = []
        self.prediction_list = []
        self.accuracies = []
        self.dates = []
        self.prediction_for_accuracy = 0
        self.points_for_median_accuracy = cnf.POINTS_FOR_MEDIAN_ACCURACY
        self.running_accuracy = 0
        self.median_accuracy = 0
        self.prediction_date = None
        self.features = features
        self.n_steps = n_steps
        self.threshold = threshold
    
    def get_single_prediction_accuracy(self, prediction_for_accuracy, real_value):
        accuracy = 0
        if real_value < prediction_for_accuracy:
            accuracy = real_value/prediction_for_accuracy
        else:
            accuracy = prediction_for_accuracy/real_value
                    
        return accuracy