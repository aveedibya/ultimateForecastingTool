# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 11:26:17 2018

@author: agarw
"""
import plotly.plotly as ply
import pandas as pd
#import cufflinks as cf
import matplotlib
from plotly.plotly import plot_mpl
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from matplotlib import pyplot as plt
plt.figure(figsize=(1,1))
#----
figure(num=None, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(18.5, 10.5, forward=True)

df = pd.read_csv('C:\\Users\\agarw\\Documents\\transaction_data.csv').dropna()
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')

#df.plot(title="Historical Transactions")
plt.figure(figsize=(25,25))
plt.plot(df[df.columns[0]], df[df.columns[1]])

df = df.set_index(df.columns[0])
result = seasonal_decompose(df, model='additive')
fig = result.plot()

result.resid
result.seasonal
result.trend

from statsmodels.tsa.arima_model import ARIMA
model = ARIMA(df, order=(7,1,0))
model_fit = model.fit(disp=0)
print(model_fit.summary())
output = model_fit.forecast()

#------------------------------------
import fbprophet
m = fbprophet.Prophet()
df = df.rename(columns={df.columns[0]:'ds', df.columns[1]:'y'})
m.fit(df)

future = m.make_future_dataframe(periods=365)
future.tail()

forecast = m.predict(future)
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

fig1 = m.plot(forecast)
fig2 = m.plot_components(forecast)
