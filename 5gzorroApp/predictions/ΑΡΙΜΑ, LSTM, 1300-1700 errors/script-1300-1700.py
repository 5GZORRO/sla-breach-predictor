# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 13:55:12 2021

@author: dlaskaratos
"""

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as md

lstm_errors = pd.read_csv('lstm-errors.csv')
arima_errors = pd.read_csv('arima-errors.csv')
lstm_errors = lstm_errors[1300:1700]
arima_errors = arima_errors[1300:1700]
lstm_mean = np.abs(lstm_errors['0'].mean())
arima_mean = np.abs(arima_errors['0'].mean())
lstm_errors = lstm_errors['0'].to_numpy().tolist()
arima_errors = arima_errors['0'].to_numpy().tolist()


true_values = pd.read_csv('test_data.csv')
dates = list()
timestamps = true_values['time']
timestamps = timestamps[1300:1700].to_numpy().tolist()

for i in range(0, len(timestamps)):
    timestamp = str(timestamps[i])[:-5]
    timestamp = int(timestamp)
    date = datetime.fromtimestamp(timestamp)#.strftime("%H:%M:%S")
    dates.append(date)

datenums=md.date2num(dates)



figure1 = plt.figure(figsize=(15 ,5))
xfmt = md.DateFormatter('%H:%M')
ax=plt.gca()
ax.xaxis.set_major_formatter(xfmt)
plt.plot(datenums, lstm_errors, "r", linewidth=0.7, label="LSTM")
plt.plot(datenums, arima_errors, "b", linewidth=0.7, label="ARIMA")
plt.plot([], [], ' ', label="ARIMA MAE: "+str(arima_mean))
plt.plot([], [], ' ', label="LSTM MAE: "+str(lstm_mean))
figure1.legend(loc="lower left")
plt.title('LSTM & ARIMA Absolute Error for the interval [1300-1700]')
plt.xlabel('Time Steps')
plt.ylabel('Absolute Error')
figure1.savefig('abs-error.png')