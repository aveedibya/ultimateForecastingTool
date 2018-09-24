# -*- coding: utf-8 -*-
"""
Created on Tue Aug 21 16:31:25 2018
@author: Aveedibya Dey
"""
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
import fbprophet
#from pyramid.arima import auto_arima

def forecast_ARIMA(df,p=1,d=0,q=1,model_type='additive', fcst_range=90):
    '''
    '''
    from statsmodels.tsa.arima_model import ARIMA
    
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    df = df.set_index(df.columns[0])
    decomposed_df = seasonal_decompose(df, model=model_type)
    #fig = result.plot()
    model = ARIMA(df, order=(p,d,q))
    model_fit = model.fit(disp=0)
    output_fcst = model_fit.forecast(fcst_range)
    
    print(model_fit.summary())
    
    return output_fcst, decomposed_df, model_fit

#------------------------------------
def forecast_FBProphet(df, dscolumn=0, ycolumn=1, futureperiod=365):
    '''
    '''
    m = fbprophet.Prophet()
    df = df.rename(columns={df.columns[dscolumn]:'ds', df.columns[ycolumn]:'y'})
    m.fit(df)
    
    future = m.make_future_dataframe(periods=futureperiod)
    #future.tail()
    forecast = m.predict(future)
    #forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()
    print("----------FB Prophet Model Run Complete--------------")
    print(forecast.tail())
    return forecast
    
#------------------------------------
#Auto Arima
# =============================================================================
# def forecast_AutoARIMA(data, datecolumn=0, timeseriescolumn=1, futureperiod=90):
#     '''
#     '''
#     stepwise_model = auto_arima(data, start_p=1, start_q=1,
#                            max_p=7, max_q=7, m=12,
#                            start_P=0, seasonal=True,
#                            d=1, trace=True,
#                            error_action='ignore',  
#                            suppress_warnings=True, 
#                            stepwise=True)
#     #train model
#     stepwise_model.fit(data[data.columns[timeseriescolumn]])
#     #forecast
#     future_forecast = stepwise_model.predict(n_periods=futureperiod)
#     print(stepwise_model.aic())
#     return future_forecast
# =============================================================================
