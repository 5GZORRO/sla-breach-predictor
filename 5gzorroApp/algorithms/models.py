# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 16:05:06 2020

@author: dlaskaratos ICOM
"""


from __future__ import annotations
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Bidirectional, LSTM, Dense
import statsmodels.api as sm
from config.config import Config as cnf
from file.file_manager import FileManager as fm
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
from datetime import datetime
from exceptions.exceptions import PathNotFoundException


class ModelEntity(ABC):
    
    def __init__(self):
        self.model = None
        self.id = None
        self.threshold = 0
        self.metric = None
        self.accuracy = 0
        self.model_available = False
        self.new_model = False
        self.active_training = False
        self.active_prediction = False
        
    @abstractmethod
    def train(self):
        pass
    
    @abstractmethod
    def predict(self):
        pass
    
    @abstractmethod
    def print_header(self):
        pass
    
    @abstractmethod
    def get_specification(params) -> ModelEntity:
        pass
    
    def get_model(self):
        return self.model
    
    def set_model(self, _model):
        self.model = _model
        
    def set_id(self, _id :str):
        self.id = _id
        
    def get_id(self):
        return self.id
    
class BaseLSTM(ModelEntity):
    
    name = 'LSTM'
    algorithm_type = 'BaseLSTM'
    n_features = 0
   
    def split_sequence(self, sequence, n_steps):
        pass
    
    def extract_data(self, srv):
        pass
    
    def name(self):
        return self.name
    
    
    
    def __init__(self, model_data):
        super().__init__()
        if model_data is not None:
            n_features = model_data.get('n_features')
            optimizer = model_data.get('optimizer')
            loss = model_data.get('loss')
            activation = model_data.get('activation')
            n_steps = model_data.get('n_steps')
            out = model_data.get('out')
            self.n_features = n_features if n_features != None else self.n_features
            self.n_steps = n_steps if n_steps != None else self.n_steps
            self.out = out if out != None else self.out
            self.optimizer = optimizer if optimizer != None else self.optimizer
            self.loss = loss if loss != None else self.loss
            self.activation = activation if activation != None else self.activation
        self.model = Sequential()
        self.model.add(Bidirectional(LSTM(self.units, 
                                          activation = self.activation), 
                                          input_shape=(self.n_steps, self.n_features)))
        self.model.add(Dense(self.out))
        self.model.compile(optimizer = self.optimizer, loss = self.loss)
        
        
    
    def get_specification(model_data) -> ModelEntity:
        spec = model_data.get('spec')
        if spec == 'univariate':
            return UnivariateLSTM(model_data)
        else:
            return MultivariateLSTM(model_data)
        
    
    def print_header(self):
        print("This is ", self.algorithm_type, " with n_features: ", self.n_features)
        
    
    
    def train(self, data = None, attr = None):
        print("TRAINING STARTED:   ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        data_path = cnf.DATA
        if fm.path_exists(data_path):
            data = pd.read_csv(data_path+"/"+'logfile.log')
        else:
            raise PathNotFoundException(str(data_path))
         
        server = "216.66.13.235:8088"
        srv = data.loc[data['server'] == server]
        train,test = self.extract_data(srv)
        X, y = self.split_sequence(train, self.n_steps)
        X = X.reshape((X.shape[0], X.shape[1], self.n_features))
        self.model.fit(X, y, epochs=200, verbose=0)
        print("TRAINING ENDED:   ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        # self.predict()
        # test = test.to_numpy().tolist()
        # bwcol = train.to_numpy()
        # bwrow = bwcol.tolist()
        # dataset = bwcol.reshape(-1, 1)
        # scaler = MinMaxScaler(feature_range=(-1, 1))
        # scaler.fit(dataset)
        # new = scaler.transform(dataset)
        
        # trans_list = list()
        # for i in range(len(new)):
        #     trans_list.append(new[i][0])

    
    def predict(self):
        print("STARTED PREDICTION:  " , datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        errors = list()
        data = pd.read_csv('data/logfile.log')
        server = "216.66.13.235:8088"
        srv = data.loc[data['server'] == server]
        train, test = self.extract_data(srv)
        x_input = train[-self.n_steps:]
        iterations = len(test)

        for i in range(iterations):
            X = np.array([x_input[i:i+self.n_steps]])
            inp = X.reshape((X.shape[0], X.shape[1], self.n_features))
            yhat = self.model.predict(inp, verbose=0)
            real_value = test[i:i+self.out]
            x_input.append(real_value[0])
            error = np.abs(yhat[0]-real_value[0])
            errors.append(error)
            
        print("ENDED PREDICTION:  " , datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        print('Mean error: ', sum(errors)/len(errors))
        
        # steps_ahead = self.out
        # count = 0
        # predictions = list()
        # predict_norm = list()
        # errors = list()
        # error_list = [0] * steps_ahead
        # test_data = pd.read_csv(data_path+'test_data.csv')
        # test_data = test_data['bw']
        # data = pd.read_csv(data_path+'logfile.log')
        # server = "216.66.13.235:8088"
        # srv = data.loc[data['server'] == server]
        # lim = int(np.round(0.6*len(srv['bw'])))
        # train = srv['bw'].head(lim)
        # x_input = train[-self.n_steps:].to_numpy()
        # # iterations = 1
        # iterations = len(test_data)
        
        # scaler = MinMaxScaler(feature_range=(-1, 1))        
        # dataset = x_input.reshape(-1, 1)
        # scaler.fit(dataset)
        # x_input = scaler.transform(dataset)
        
        # x_input = x_input.tolist()
        
        # for i in range(iterations):
        #      count = count + 1
        #      X = np.array([x_input[i:i+self.n_steps]])
        #      inp = X.reshape((X.shape[0], X.shape[1], self.n_features))
        #      yhat = self.model.predict(inp, verbose=0)
        #      # predict_norm.append(yhat.tolist()[0])
        #      real_values = test_data[i:i + steps_ahead].to_numpy().tolist()
        #      x_input.extend(real_values)
        #      predictions.extend(yhat.tolist()[0])
        #      error = np.abs(np.subtract(yhat.tolist()[0], real_values))
        #      errors.append(error)
        # predictions.append(yhat.tolist()[0])

        # pred_norm = scaler.inverse_transform(np.array(predict_norm).reshape(-1, 1)).tolist()
        # for i in range(len(pred_norm)):
        #     predictions.append(pred_norm[i][0])
        # error_list = np.abs(np.subtract(predictions, real_values))
        # avg_error = sum(error_list)/self.out
        # pd.DataFrame(predictions).to_csv(str(self.n_steps)+'-'+str(self.out)+'predictions-norm.csv')
        # pd.DataFrame(error_list).to_csv(str(self.n_steps)+'-'+str(self.out)+'errors-norm.csv')

        
        # path = create_path_if_not_exists('predictions/lstm')
        # pd.DataFrame(predictions).to_csv((str(self.n_steps)+"-"+str(self.out)+"-"+'predictions.csv'))
        # pd.DataFrame(error_list).to_csv((str(self.n_steps)+"-"+str(self.out)+"-"+'errors.csv'))
        # print("PREDICTION ENDED:   ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        # Print the average error for every time step
        # print("Mean error per step-ahead: ", sum(errors)/count)
        # print("Mean error: ", avg_error)
        # self.calculate_and_plot_error(predictions, real_values, error_list)
    
    def calculate_and_plot_error(self, predictions, test_data, errors):
        print("PLOTTING STARTED:   ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

        figure1 = plt.figure(figsize=(15 ,5))
        plt.plot(test_data, "r", label="Real Values")
        plt.plot(predictions, "b", label="Predictions")
        # plt.ylim(0, 5000)
        plt.plot(errors, "g", label="Absolute Error")
        plt.title(str(self.n_steps)+'-'+str(self.out)+' Prediction & Error')
        plt.xlabel('Time')
        plt.ylabel('Bandwidth (Mbps)')
        figure1.legend(loc="lower left")
        plt.grid(True)
        figure1.savefig(str(self.n_steps)+'-'+str(self.out)+'.png')
        
        print("PLOTTING ENDED:  ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        

class UnivariateLSTM(BaseLSTM):
    
    name = 'univariate'
    base = 'lstm'
    n_steps = 3
    out = 1
    n_features = 1
    units = 100
    confidence = 95
    activation = 'relu'
    merge_mode = 'concat'
    optimizer = 'adam'
    loss = 'mse'
    algorithm_type = 'UnivariateLSTM'
    
    def split_sequence(self, sequence, n_steps):
        
        X, y = list(), list()
        for i in range(len(sequence)):
            end_ix = i + n_steps
            if end_ix > len(sequence)-self.out:
                break
            seq_x, seq_y = sequence[i:end_ix], sequence[end_ix:end_ix+self.out]
            X.append(seq_x)
            y.append(seq_y)
        return np.array(X), np.array(y)
    
    def extract_data(self, srv):
        lim = int(np.round(0.6*len(srv['bw'])))
        train = srv['bw'].head(lim)
        test = srv['bw'][lim:]
        train = train.to_numpy().tolist()
        test = test.to_numpy().tolist()
        return train, test
    
    def predict(self, data):
        X = np.array([data])
        inp = X.reshape((X.shape[0], X.shape[1], self.n_features))
        yhat = self.model.predict(inp, verbose=0)
        prediction = yhat[0][0]
        return prediction
        # print("STARTED PREDICTION FOR UNIVARIATE LSTM:  " , datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        # predictions = list()
        # steps_ahead = self.out
        # # errors = [0] * steps_ahead
        # # error_list = list()
        # errors = list()
        # data = pd.read_csv('data/logfile.log')
        # server = "216.66.13.235:8088"
        # srv = data.loc[data['server'] == server]
        # train, test = self.extract_data(srv)
        # x_input = train[-self.n_steps:]
        # iterations = len(test)
        # count = 0
        
        # for i in range(iterations -steps_ahead +1):
        #       count = count + 1
        #       X = np.array([x_input[i  :i + self.n_steps]])
        #       inp = X.reshape((X.shape[0], X.shape[1], self.n_features))
        #       yhat = self.model.predict(inp, verbose=0)
        #       real_values = test[i : i + steps_ahead]
        #       x_input.extend(real_values)
        #       predictions.extend(yhat[0])
        #       error = np.abs(np.subtract(yhat[0], real_values))
        #       errors.append(error)
        #       # errors = np.array(error) + np.array(errors)
        #       # error_list.append(error[0])

        # print("ENDED PREDICTION FOR UNIVARIATE LSTM:  " , datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        # # print('Mean error per step ahead: ', np.array(errors)/count)
        # print('Mean error per step ahead: ', sum(errors)/len(errors))
        # # self.calculate_and_plot_error(predictions, test, errors)
    

class MultivariateLSTM(BaseLSTM):
    
    _type = 'multivariate'
    n_steps = 3
    out = 1
    n_features = 4
    units = 200
    confidence = 95
    activation = 'relu'
    merge_mode = 'concat'
    optimizer = 'adam'
    loss = 'mse'
    algorithm_type = 'MutilvariateLSTM'
        
    def split_sequence(self, sequence, n_steps):
       
         X, y = list(), list()
         for i in range(len(sequence)):
              end_ix = i + n_steps
              if end_ix > len(sequence):
                   break
              seq_x, seq_y = sequence[i:end_ix, :-1], sequence[end_ix-1, -1]
              X.append(seq_x)
              y.append(seq_y)
         return np.array(X), np.array(y)
     
    def extract_data(self, srv):
        srv = srv.drop(columns=['server'])
        arrange = ['requests', 'hits ', 'bw']
        srv = srv[arrange]
        srv['o'] = srv['bw'].shift(-1)
        srv = srv.dropna()
        lim = int(np.round(0.6*len(srv['bw'])))
        train = srv.head(lim)
        test = srv[lim:]
        return train.to_numpy(), test.to_numpy()
    
    def predict(self):
        print("STARTED PREDICTION FOR MULTIVARIATE LSTM:  " , datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        predictions = list()
        data = pd.read_csv('data/logfile.log')
        server = "216.66.13.235:8088"
        srv = data.loc[data['server'] == server]
        lim = int(np.round(0.6*len(srv['bw'])))
        real_values = srv['bw'][lim+self.n_steps:].to_numpy().tolist()
        train, test = self.extract_data(srv)
        # Xx, Yy = self.split_sequence(test, self.n_steps)
        # x_input = Xx
        # # x_input = np.array([test[0:self.n_steps][:, :-1]])
        # x_input = x_input.reshape((x_input.shape[0], x_input.shape[1], self.n_features))
        # yhat = self.model.predict(x_input, verbose=0)
        # print(len(yhat))

        x_input = train[0:self.n_steps][:, :-1]
        iterations = len(test)
        
        for i in range(iterations-self.n_steps):
            X = np.array([x_input[i:self.n_steps+i]])
            X = X.reshape((X.shape[0], X.shape[1], self.n_features))
            yhat = self.model.predict(X, verbose=0)
            inp = test[i:self.n_steps+i, :-1]
            x_input = np.vstack((x_input, inp[0]))
            predictions.append(yhat[0][0])
        
        # errors = np.abs(Yy-yhat.flatten())
        errors = np.abs(np.subtract(predictions, real_values))
        pd.DataFrame(predictions).to_csv('multivariate-predictions-iterable.csv')
        print("ENDED PREDICTION:  " , datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        print('Mean error: ', sum(errors)/len(errors))
        self.calculate_and_plot_error(predictions, real_values, errors)
    

class BaseARIMA(ModelEntity):
    
    algorithm_type = 'BaseARIMA'
    out = 0
    n_steps = 0
    
    def __init__(self, model_data):
        super().__init__()
        self.model = None
        self.result = None
        self.out = model_data.get('steps_ahead')
    
    def get_specification(model_data):
        return SARIMAX(model_data)
    
    def print_header(self):
        print("This is ", self.algorithm_type)
       

class SARIMAX(BaseARIMA):
    
    algorithm_type = 'SARIMAX'
    
    def __init__(self, model_data):
        super().__init__(model_data)
    
    def train(self, data, attr = None):
        
        print("TRAINING STARTED:   ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        # if not attr:
        #     raise AttributeListCannotBeEmptyException()
            
        data_path = cnf.DATA
        path = fm.create_path_if_not_exists(data_path)
            
        data = pd.read_csv(path/'logfile.log')
        server = '216.66.13.235:8088'
        srv = data.loc[data['server'] == server]
        lim = int(np.round(0.6*len(srv['bw'])))
        train = srv['bw'].head(lim)
        test = srv['bw'][lim:]
        exog = srv[['requests', 'hits ']]
        
        self.model = sm.tsa.statespace.SARIMAX(train, exog = exog.head(lim), enforce_stationarity = True, trend = 'n', order = (1,1,1))
        self.result = self.model.fit(disp = False)
        self.predict(test, self.result, exog, lim, train)
        print("TRAINING ENDED:   ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        return self.model
        
    
    def predict(self, test, result, exog, lim, train):
        print("PREDICTION STARTED:   ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        out = self.out
        pd.plotting.register_matplotlib_converters()
        test = test[0:out]
       
        predict = self.result.get_prediction(lim, lim+out-1, dynamic = True, exog = exog[lim:lim+out])
        pd.DataFrame(predict.predicted_mean).reset_index(drop = True).to_csv("arima-1-1-1-predictions.csv")
        predicted_list = predict.predicted_mean.tolist()
        test = test.to_numpy().tolist()
        abs_error = np.abs(np.subtract(test, predicted_list))
        pd.DataFrame(abs_error).to_csv('arima-1-1-1-errors.csv')
        mean_error = abs_error.mean()
        print('Mean error for SARIMAX: ', str(mean_error))
        print("PREDICTION ENDED:   ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        
        # figure1 = plt.figure(figsize=(15 ,5))
        # plt.plot(test, "r", label="Actual Data")
        # plt.plot(predicted_list, 'g', label="Predictions")
        # plt.plot(abs_error, 'b', label = "Aboslute Error")
        # plt.legend(loc="lower left")
        # figure1.savefig("predictions/arima-30-predictions-ahead.png")
    
    
        