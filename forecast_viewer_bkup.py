# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 10:26:09 2018

@author: agarw
"""
import forecast_example as fcst
import dash_core_components as dcc
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
import dash
import dash_html_components as html
import datetime as dt
import calendar
import numpy as np
from plotly.plotly import plot_mpl
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima_model import ARIMA

df = pd.read_csv('C:\\Users\\agarw\\Documents\\transaction_data.csv').dropna()
df_final = fcst.fcst_wklyavg(df)

df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
df = df.set_index(df.columns[0])
result = seasonal_decompose(df, model='additive')
result_trend = result.trend.dropna().reset_index()
result_seasonal = result.seasonal.dropna().reset_index()
result_resid = result.resid.dropna().reset_index()
#fig = result.plot()
#unique_url = plot_mpl(fig)

trace_actuals = go.Scatter(
    x = df_final['Date'],
    y = df_final['Volume'],
    mode = 'lines+markers',
    name = 'actuals')

trace_forecast = go.Scatter(
    x = df_final[df_final['Forecast']>0]['Date'],
    y = df_final[df_final['Forecast']>0]['Forecast'],
    mode = 'lines+markers',
    name = 'forecast')

trace_trend =  go.Scatter(
    x = result_trend[result_trend.columns[0]],
    y = result_trend[result_trend.columns[1]],
    mode = 'lines',
    name = 'trend')

trace_seasonal =  go.Scatter(
    x = result_seasonal[result_seasonal.columns[0]],
    y = result_seasonal[result_seasonal.columns[1]],
    mode = 'lines',
    name = 'seasonal')

trace_residual =  go.Scatter(
    x = result_resid[result_resid.columns[0]],
    y = result_resid[result_resid.columns[1]],
    mode = 'lines',
    name = 'residual')

print(result.resid.dropna().index)
print(result.resid.dropna()[result.resid.columns[0]].head())

app = dash.Dash()

date_dict = []
values_date_default = []
for month in df_final['Date'].dt.month.unique():
    date_dict.append({'label': calendar.month_abbr[month], 'value': month})
    values_date_default.append(month)

app.layout = html.Div(children=[
        html.Div([dcc.Markdown(children='''### Forecast Viewer: 
***
__Quick Description__: Forecast generator and viewer. Shows monthly and daily level views of forecast with interactive filters. 
***
''')]),
       # html.Div(children='Chart showing actuals and forecasts', style={'textAlign': 'center'}),
        html.Div([
                html.Div([html.Strong(["Monthly View of Forecast and Actuals"]), dcc.Graph(id='monthly_view')], style={'width': '45%', 'display': 'inline-block', 'padding': '0', 'background-color': '#e0e0eb'}),
                html.Div([], style={'width': '5%', 'display': 'inline-flex', 'padding': '20 20', 'background-color': '#e0e0eb'}),
                html.Div([html.Strong(["Daily View of Forecast and Actuals"]), dcc.Graph(id='graph-with-slider')], style={'width': '45%', 'display': 'inline-block', 'padding': '20 20', 'background-color': '#e0e0eb'})
                ]),
        #dcc.Slider(id='date-slider', min=df_final['Date'].dt.month.min(), max=df_final['Date'].dt.month.max(), value=df_final['Date'].dt.month.min(), step=None, marks={str(month): calendar.month_abbr[month] for month in df_final['Date'].dt.month.unique()}),
         
        html.Div([html.Label('Choose Month:'), dcc.Dropdown(id='date-dropdown', options=date_dict, value=values_date_default, multi=True)], style={'width': '45%', 'display': 'inline-flex', 'padding': '20 20', 'background-color': '#e0e0eb'}),
        html.Div([], style={'width': '5%', 'display': 'inline-flex', 'padding': '20 20', 'background-color': '#e0e0eb'}),
        html.Div([html.Label('Choose Data to Show:'), dcc.RadioItems(id='dataselector', options=[
                        {'label': 'View Data Only', 'value': 1},
                        {'label': 'View Data and Forecast', 'value': 2},
                        {'label': 'View Forcast Only', 'value': 3}
                        ], value=2)
                ], style={'width': '45%', 'display': 'inline-flex', 'padding': '20 20', 'background-color': '#e0e0eb'}),
        html.Div([dcc.Graph(id='trend_view', figure={'data':[trace_trend], 'layout':{'title':'Time Series Trend Plot'}}, style={'height': 300}),
                  dcc.Graph(id='seasonal_view', figure={'data':[trace_seasonal], 'layout':{'title':'Time Series Seasonal Plot'}}, style={'height': 300}),
                  dcc.Graph(id='residual_view', figure={'data':[trace_residual], 'layout':{'title':'Time Series Residual Plot'}}, style={'height': 300})], style={'width': '45%'})

    ])
    
    
"""html.Div([
html.Div(dcc.Input(id='input-box', type='text')),
html.Button('Submit', id='button'),
html.Div(id='output-container-button',
         children='Enter # of days to forecast and press submit')
]),"""


    
@app.callback(
    dash.dependencies.Output('monthly_view', 'figure'),
    [dash.dependencies.Input('date-dropdown', 'value'),
     dash.dependencies.Input('dataselector', 'value')])

def update_monthly_view(selected_month, dataselected):
    df_final_monthly = df_final.groupby('Month').agg({'Volume':np.sum, 'Forecast':np.sum}).reset_index()
    filtered_df = df_final_monthly[df_final_monthly['Month'].isin(selected_month)]
    traces = []
    month_list = []
    for i in selected_month:
        month_list.append(calendar.month_abbr[i])
    
    if dataselected !=3:
        traces.append(go.Bar(
                x=filtered_df[filtered_df['Volume']>0]['Month'],
                y=filtered_df[filtered_df['Volume']>0]['Volume'],
                text=filtered_df[filtered_df['Volume']>0]['Month'].apply(lambda x: calendar.month_name[x]),
                customdata=filtered_df[filtered_df['Volume']>0]['Month'],
                name='Actuals'
            ))
    if dataselected !=1:
        traces.append(go.Bar(
            x=filtered_df[filtered_df['Forecast']>0]['Month'],
            y=filtered_df[filtered_df['Forecast']>0]['Forecast'],
            text=filtered_df[filtered_df['Forecast']>0]['Month'].apply(lambda x: calendar.month_name[x]),
            customdata=filtered_df[filtered_df['Forecast']>0]['Month'],
            name='Forecast'
            ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'title': 'Dates selected: ' + ",".join(month_list)},
            yaxis={'title': 'Volume'},
            barmode='stack'
        )
    }
    
@app.callback(
    dash.dependencies.Output('graph-with-slider', 'figure'),
    [dash.dependencies.Input('date-dropdown', 'value'),
     dash.dependencies.Input('dataselector', 'value')])
     #dash.dependencies.Input('button', 'n_clicks')],
    #[dash.dependencies.State('input-box', 'value')])

def update_daily_view(selected_month, dataselected):
    #if fcst_range_entered > 0:
    #    df_final = fcst.fcst_wklyavg(df, fcst_range=int(fcst_range_entered))
    filtered_df = df_final[df_final['Date'].dt.month.isin(selected_month)]
    traces = []
    month_list = []
    for i in selected_month:
        month_list.append(calendar.month_abbr[i])
    
    if dataselected !=3:
        traces.append(go.Scatter(
                x=filtered_df[filtered_df['Volume']>0]['Date'],
                y=filtered_df[filtered_df['Volume']>0]['Volume'],
                mode='lines+markers', name='Actuals for: '+",".join(month_list)
            ))
    if dataselected !=1:
        traces.append(go.Scatter(
            x=filtered_df[filtered_df['Forecast']>0]['Date'],
            y=filtered_df[filtered_df['Forecast']>0]['Forecast'],
            mode='lines+markers', name='Forecast for: ' + ",".join(month_list)
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'title': 'Dates selected: ' + ",".join(month_list)},
            yaxis={'title': 'Volume'},
            #margin={'l': 40, 'b': 30, 't': 40, 'r': 0},
            #legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

if __name__ == '__main__':
    app.run_server(debug=True)