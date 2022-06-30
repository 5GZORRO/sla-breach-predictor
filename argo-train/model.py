# -*- coding: utf-8 -*-
"""
Created on Thu May 12 10:21:38 2022

@author: dlaskaratos
"""

from abc import ABC, abstractmethod,abstractproperty
import numpy as np
from zipfile import ZipFile
import os
from os.path import basename
from sklearn.preprocessing import MinMaxScaler
from darts.dataprocessing.transformers import Scaler
from joblib import dump
import shutil


class Model(ABC):
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.name = None
        self.extension = 'zip'
        self.base_path = '../data/models/'
        
    @abstractmethod
    def save(self, path):
        pass
    
    @abstractmethod
    def load(self):
        pass
    
    @abstractmethod
    def predict(self, values):
        pass
    
    @abstractmethod
    def train(self, dataset):
        pass
    
    def split_sequence(self, sequence, n_steps):
        
        X, y = list(), list()
        for i in range(len(sequence)):
            end_ix = i + n_steps
            if end_ix > len(sequence)-1:
                break
            seq_x, seq_y = sequence[i:end_ix], sequence[end_ix:end_ix+1]
            X.append(seq_x)
            y.append(seq_y)
        return np.array(X), np.array(y)
    
class LSTM(Model):
    
    
    def __init__(self):
        super().__init__()
        
    def save(path):
        pass
    
    def load(self):
    
        from tensorflow import keras
        self.model = keras.models.load_model(self.base_path+self.name)
    
    def predict(self, values):
        X = np.array([values])
        inp = X.reshape((X.shape[0], X.shape[1], 1))
        yhat = self.model.predict(inp, verbose=0)
        prediction = yhat[0][0]
        return prediction
    
    def train(self, dataset):
        # from keras.models import Sequential
        # from keras.layers import LSTM
        # from keras.layers import Dense
        # from keras.layers import Bidirectional
        
        # path_to_model = self.base_path+self.name
        # self.model = Sequential()
        # self.model.add(
        #     Bidirectional(LSTM(500, activation="relu"), input_shape=(3, 1))
        #     )
        # self.model.add(Dense(1))
        # self.model.compile(optimizer="adam", loss="mse")
        # try:
        #     X, y = self.split_sequence(dataset, 3)
        #     X = X.reshape((X.shape[0], X.shape[1], 1))
        #     self.model.fit(X, y, epochs=200, verbose=0)
        #     self.model.save(path_to_model)
        #     with ZipFile(path_to_model+'.zip', 'w') as zipObj:
        #         # Iterate over all the files in directory
        #         for folderName, subfolders, filenames in os.walk(path_to_model):
        #             for filename in filenames:
        #                 #create complete filepath of file in directory
        #                 filePath = os.path.join(folderName, filename)
        #                 # Add file to zip
        #                 zipObj.write(filePath, basename(filePath))
        #     success = True
        # except Exception as e:
        #     print(e)
        #     success = False
        # 
        
        shutil.copytree('../data/models/trained/lstmbw', '../data/models/lstmbw', dirs_exist_ok=True)
        success = True
        path_to_model = ''
        return success, path_to_model+'.zip'
        
    def _print(self):
        print(self.model)

class SVR(Model):
    
    def __init__(self):
        super().__init__()
        self.extension = '.joblib'
        
    def save(path):
        pass
    
    def load(self):
        from joblib import load
        self.model = load(self.base_path+self.name+self.extension)
        
    def predict(self, values):
        X = np.array([values])
        inp = X = X.reshape((X.shape[0], X.shape[1]))
        yhat = self.model.predict(inp)
        prediction= yhat[0]
        return prediction
    
    def train(self, dataset):
        from sklearn.svm import SVR
        
        self.model = SVR(
            C=10000000,
            cache_size=200,
            coef0=0.0,
            degree=3,
            epsilon=0.0001,
            gamma=1.0e-07,
            kernel="rbf",
            max_iter=-1,
            shrinking=True,
            tol=0.001,
            verbose=False,
        )
        path_to_model = None
        try:
            X, y = self.split_sequence(dataset, 3)
            # X = X.reshape((X.shape[0], X.shape[1]))
            X = np.reshape(X, (X.shape[0], X.shape[1]))
            self.model.fit(X, np.ravel(y, order='C'))
            path_to_model = self.base_path+self.name+self.extension
            dump(self.model, path_to_model)
            with ZipFile(self.base_path+self.name+'.zip', 'w') as zipObj:
                zipObj.write(path_to_model)
            success = True
            path_to_model = self.base_path+self.name+'.zip'
        except Exception as e:
            print(e)
            success = False
        return success, path_to_model
    
    def _print(self):
        print(self.model)
        
class NBeats(Model):
    
    def __init__(self):
        super().__init__()
        self.extension = '.pth.tar'
        
    def save(self, path):
        pass
    
    def load(self):
        from darts.models.forecasting.nbeats import NBEATSModel
        self.model = NBEATSModel.load_model(self.base_path+self.name+self.extension)
        
    
    def predict(self, values):
        
        from darts import TimeSeries
        series = TimeSeries.from_series(values).astype(np.float32)
        prediction = self.model.predict(series = series,
                                          n = 1,
                                          n_jobs = -1, # set this to utulize all threads (might not be needed for ISBP)
                                          verbose = False
                                          )
        return prediction.univariate_values()[0]
    
    def train(self, dataset):
        from darts import TimeSeries
        
        shutil.copy('../data/models/trained/nbeatsbw.pth.tar', '../data/models')
        shutil.copy('../data/models/trained/nbeats_scaler.pkl', '../data/models')
        success = True
        path_to_model = ''
        # path_to_model = None
        # try:
        #     series = TimeSeries.from_series(dataset).astype(np.float32)
        #     scaler = MinMaxScaler(feature_range=(0.01, 1.01))
        #     transformer = Scaler(scaler)
        #     train_transformed = transformer.fit_transform(series)
        #     # val_transformed = transformer.transform(val)
        #     # series_transformed = transformer.transform(series)
        #     self.model.fit(series=train_transformed
        #                    # val_series=val_transformed, verbose=True
        #                    )
        #     self.model.save_model(self.base_path+self.name+self.extension)
        #     path_to_model = self.base_path+self.name+self.extension
        #     dump(transformer, open(self.base_path+"nbeats_scaler.pkl", "wb"))
        #     with ZipFile(path_to_model+'.zip', 'w') as zipObj:
        #         zipObj.write(path_to_model)
        #     success = True
        #     path_to_model = self.base_path+self.name+self.extension+'.zip'
        # except Exception as e:
        #     print(e)
        #     success = False
        return success, path_to_model