# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 16:56:52 2018

@author: agarw
"""

import pandas as pd
import numpy as np
import datetime

#df = pd.read_csv('C:\\Users\\agarw\\Documents\\transaction_data.csv').dropna()

def fcst_wklyavg(df, fcst_range=90, n_week=6, stop_at_futuredates=0, data_period=7):

    #df = pd.read_csv('C:\\Users\\agarw\\Documents\\transaction_data.csv').dropna()
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    
    #fcst_range = 90
    fcst_start = max(df['Date']) + datetime.timedelta(days=1)
    fcst_end = max(df['Date']) + datetime.timedelta(days=fcst_range)
    
    df2 = pd.DataFrame({'Date': pd.date_range(fcst_start, fcst_end, freq='D')})
    df2['Volume'] = None
    
    df_final = pd.concat([df, df2]).reset_index().drop('index', axis=1)
    
    df_final['Forecast'] = 0.0
    
    if stop_at_futuredates == 0:
        #n-week average:
        n = n_week
        
        for i in (range(df.shape[0], df_final.shape[0])):
            curr_count = 0.0
            curr_sum = 0.0
            for j in range(1, int(n+1)):
                #print("i is:",i)
                #print("j is:",j)
                if np.isnan(df_final['Volume'][i-j*data_period]):
                    if np.isnan(df_final['Forecast'][i-j*data_period]) == False:
                        curr_sum += df_final['Forecast'][i-j*data_period]
                        curr_count += 1
                        #print("Forecast value taken:",df_final['Forecast'][i-j*7])
                else:
                    curr_sum += df_final['Volume'][i-j*data_period]
                    curr_count += 1
                    #print("Volume value taken:",df_final['Volume'][i-j*7])
            df_final['Forecast'][i] = curr_sum/curr_count
            #print(curr_sum, curr_count)
        
        #Add year to dataframe
        df_final['Year'] = df_final['Date'].dt.year
        #Add month to dataframe
        df_final['Month'] = df_final['Date'].dt.month
        #Add weekday name in the dataframe
        df_final['WkdyNm'] = df_final['Date'].dt.weekday_name
    print('------------------Moving Average Forecast Generated-------------------')
    return df_final
    

    