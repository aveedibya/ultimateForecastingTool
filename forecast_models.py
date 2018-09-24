# -*- coding: utf-8 -*-
"""
Created on Tue Aug 21 16:31:25 2018

@author: agarw
"""
import plotly.plotly as ply
import pandas as pd

from plotly.plotly import plot_mpl
from statsmodels.tsa.seasonal import seasonal_decompose

import fbprophet


def forecast_ARIMA(df,p=1,d=0,q=1,model_type='additive', fcst_range=90):
    '''
    '''
    from statsmodels.tsa.arima_model import ARIMA
    
    df = df.set_index(df.columns[0])
    decomposed_df = seasonal_decompose(df, model=model_type)
    
    model = ARIMA(df, order=(p,d,q))
    model_fit = model.fit(disp=0)
    output_fcst = model_fit.forecast(fcst_range)
    
    print(model_fit.summary())
    
    return output_fcst, decomposed_df, model_fit

#result.resid
#result.seasonal
#result.trend
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

    return forecast


