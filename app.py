# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 10:26:09 2018

@author: agarw
"""
import dash_table_experiments as dte
from parse_contents import parse_contents

import forecast_example as fcst
import dash_core_components as dcc
import plotly.graph_objs as go
import pandas as pd
import dash
import dash_html_components as html
import calendar
import forecast_models
import adjustment_block

app = dash.Dash()
app.scripts.config.serve_locally = True
app.config['suppress_callback_exceptions']=True
app.title = 'Forecasting Tool'

server = app.server

def dropdown_dict(df):
    date_dict = []
    values_date_default = []
    for month in df['Date'].dt.month.unique():
        date_dict.append({'label': calendar.month_abbr[month], 'value': month})
        values_date_default.append(month)
    print('-----------------dropdown values processed----------------------')
    return date_dict, values_date_default

#date_dict, values_date_default = dropdown_dict(df)

app.layout = html.Div(children=[
        dcc.Markdown(children='''### Forecast Generator: '''), 
        html.Div([dcc.Markdown('''__Quick Description__: Forecast generator and viewer. Shows monthly and daily level views of forecast with interactive filters. ''')], style={'borderTop': 'thin lightgrey solid', 'borderBottom': 'thin lightgrey solid', 'padding': '5'}),
        
        #Add filters for the data
        html.Div([
                html.Div([html.Label('Choose Data to Show:'), 
                dcc.RadioItems(id='dataselector', options=[
                        {'label': 'View Data Only', 'value': 1},
                        {'label': 'View Data and Forecast', 'value': 2},
                        {'label': 'View Forecast Only', 'value': 3}
                        ], value=2, labelStyle={'display': 'inline-block'})
                ], style={'width': '49%', 'display': 'inline-block'}),
                html.Div([html.Label('Choose Month:'), 
                dcc.Dropdown(id='date-dropdown', multi=True
                               #,options=date_dict, value=values_date_default, multi=True
                )], style={'width': '49%', 'display': 'inline-block', 'float': 'right'})
        ], style={'borderBottom': 'thin lightgrey dotted', 'padding': '20px 5px'}),
        
        #Graph
        html.Div([html.Div([dcc.Graph(id='graph-daily')], style={'padding': '10 10', 'display': 'inline-block', 'width': '69%'}),
                  html.Div([html.Label('Adjust Forecast:'), #----Adjust Forecast Elements
                            html.Div([
                                    html.Div([dcc.Input(id='adj-number', type='number')], style={'display': 'inline-flex'}),
                                    html.Div([html.Button('Create Adj.', id='adj-creator')], style={'display': 'inline-flex'})
                                    ], style={'width': '50%'}),
                            html.Div(children=adjustment_block.add_adj_block(3)[0])], style={'display': 'inline-block', 'width': '29%', 'float': 'top', 'vertical-align': 'top', 'padding': '5'})
                ], style={'padding': '0'}),
    
        #Choose Forecasting Model
        html.Div([html.Label('Choose Forecasting Model:'), 
                dcc.Dropdown(id='model-dropdown',
                               options=[
                        {'label': 'ARIMA Time Series', 'value': 1},
                        {'label': 'FB Prophet', 'value': 2},
                        {'label': 'Moving Average', 'value': 3}], value=3)
                ], style={}),
        
        #Take ARIMA Inputs
        html.Div([
                html.Div(dcc.Input(id='arima-p', type='number', placeholder='AR(p)='), style={'display': 'inline-block'}),
                html.Div(dcc.Input(id='arima-d', type='number', placeholder='I(d)='), style={'display': 'inline-block'}),
                html.Div(dcc.Input(id='arima-q', type='number', placeholder='MA(q)='), style={'display': 'inline-block'}),
                html.Button('Submit ARIMA Parameters ', id='arima-submit'),
                html.Div(id='output-container-button',
                         children='Enter ARIMA parameters and click Submit to refresh forecast!')], id='arima-inputblock'),
    
        #Take Moving Average Inputs
        html.Div([
                html.Div(dcc.Input(id='n_weeks', type='number', placeholder='#Week for averaging = 6'), style={'display': 'inline-block'}),
                html.Div(dcc.Input(id='period', type='number', placeholder='Period = 7'), style={'display': 'inline-block'}),
                html.Button('Update Moving Average Forecast ', id='movingavg-submit'),
                html.Div(id='output-container-button-ma',
                         children='Enter Moving Average parameters and click Submit to refresh forecast!')], id='movingavg-inputblock'),
    
        #Stores df-to-json for a forecast method
        html.Div(id='intermediate-value', style={'display': 'none'}),
        
        #Stores uploded data converted to df-to-json 
        html.Div(id='upload-data-df', style={'display': 'none'}),
        
        #Stores uploded data converted to df-to-json 
        html.Div(id='adj-forecast-df', style={'display': 'none'}),
        
        #Data Table elements
        html.Div([dcc.Upload(
                id='upload-data',
                children=html.Div(['Drag and Drop or ', html.A('Select Files')
                ]),
                style={
                    'width': '30%', 'height': '60px', 'lineHeight': '60px', 'borderWidth': '0px',
                    'borderStyle': 'solid','borderRadius': '5px', 'textAlign': 'center', 'margin-top': '20px', 
                    'backgroundColor': '#ebebe0'
                },
                # Allow multiple files to be uploaded
                multiple=True
            ),
            html.Div(id='output-data-upload'),
            html.Div(dte.DataTable(rows=[{}]), style={'display': 'none'})
        ])
#        html.Div([dcc.Graph(id='trend_view', figure={'data':[trace_trend], 'layout':{'title':'Time Series Trend Plot'}}, style={'height': 300}),
#                  dcc.Graph(id='seasonal_view', figure={'data':[trace_seasonal], 'layout':{'title':'Time Series Seasonal Plot'}}, style={'height': 300}),
#                  dcc.Graph(id='residual_view', figure={'data':[trace_residual], 'layout':{'title':'Time Series Residual Plot'}}, style={'height': 300})], style={'width': '45%'})

        ]
        #, className='container' #If you want to show everything in a shrinked smaller central section
        , style={'width': ''})

    
def return_a_textbox(value):
    '''
    '''
    if value:
        return html.Div([
                html.Div(dcc.Input(id='input-box', type='text')),
                html.Button('Submit', id='button'),
                html.Div(id='output-container-button',
                         children='Enter a value and press submit')])

#--------------------------------------------------------
#Show ARIMA input parameters block
@app.callback(
    dash.dependencies.Output('arima-inputblock', 'style'),
    [dash.dependencies.Input('model-dropdown', 'value')])

def update_arimablock(value):
    if value ==1:
        return {'display': 'block', 'padding': '20 0'}
    else:
        return {'display': 'none'}

#--------------------------------------------------------
#Show ARIMA input parameters block
@app.callback(
    dash.dependencies.Output('movingavg-inputblock', 'style'),
    [dash.dependencies.Input('model-dropdown', 'value')])

def update_movingavgblock(value):
    if value ==3:
        return {'display': 'block', 'padding': '20 0'}
    else:
        return {'display': 'none'}
    
#--------------------------------------------------------    
#Generate forecasts - Forecast dataframe is generated
@app.callback(
    dash.dependencies.Output('intermediate-value', 'children'),
    [dash.dependencies.Input('upload-data-df', 'children'),
     dash.dependencies.Input('model-dropdown', 'value'),
     dash.dependencies.Input('arima-submit', 'n_clicks'),
     dash.dependencies.Input('movingavg-submit', 'n_clicks')],
     [dash.dependencies.State('arima-p', 'value'),
      dash.dependencies.State('arima-d', 'value'),
      dash.dependencies.State('arima-q', 'value'),
      dash.dependencies.State('n_weeks', 'value'),
      dash.dependencies.State('period', 'value')])

def update_daily_view(uploaded_df, modelselected, arima_n_clicks, ma_n_clicks, arimap=1, arimad=0, arimaq=1,
                      n_weeks_ma=6, period_ma=7):
    '''
    '''
    print("-----Printing Uploaded Data------")
    print(uploaded_df)
    df = pd.read_json(uploaded_df, orient='split').dropna()
    #df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    print(df)
    if modelselected ==1: #1=ARIMA
        df_final = fcst.fcst_wklyavg(df, stop_at_futuredates=1)
        arima_fcst = forecast_models.forecast_ARIMA(df, p=arimap, d=arimad, q=arimaq)
        df_final['Forecast'][df.shape[0]:] = arima_fcst[0][0]
    elif modelselected == 2: #2= FB Prophet
        df_final = fcst.fcst_wklyavg(df, stop_at_futuredates=1)
        print('--------------Empty forecast dataframe generated-----------')
        print(df_final.tail())
        prophetfcst = forecast_models.forecast_FBProphet(df, futureperiod=90)
        df_final['Forecast'][df.shape[0]:] = prophetfcst['yhat'][df.shape[0]:]
        df_final = plot_error_range(df, df_final, prophetfcst)
        #df_final = df_final.rename(columns={'ds':'Date', 'yhat':'Forecast'})
    elif modelselected ==3: #3=Moving Average
        df_final = fcst.fcst_wklyavg(df, n_week=n_weeks_ma, data_period=period_ma)
        #print(df_final.tail())
    return df_final.to_json(date_format='iso', orient='split')

#--------------------------------------------------------
def plot_error_range(df, df_final, df_fcst, modelselected=3):
    '''
    '''
    df_final['Forecast_upper']=0.0
    df_final['Forecast_lower']=0.0
    
    if modelselected ==3: #FB Prophet Model
        df_final['Forecast_upper'][df.shape[0]:] = df_fcst['yhat_upper'][df.shape[0]:]
        df_final['Forecast_lower'][df.shape[0]:] = df_fcst['yhat_lower'][df.shape[0]:]
    print("-----error range df returned------")
    print(df_final.tail())
    return df_final        
        

#-------------------------------------------------------- 
#Update Dropdown Filter
@app.callback(
    dash.dependencies.Output('date-dropdown', 'options'),
    [dash.dependencies.Input('intermediate-value', 'children')])
     
def update_dropdown_options(json_intermediate_data):    
    '''
    '''
    print('-------------------updating dropdown filters: Options-------------------')
    print(json_intermediate_data)
    df_final = pd.read_json(json_intermediate_data, orient='split')
    print(df_final)
    date_dict, values_date_default = dropdown_dict(df_final)
    return date_dict


#-------------------------------------------------------- 
#Update Dropdown Values
@app.callback(
    dash.dependencies.Output('date-dropdown', 'value'),
    [dash.dependencies.Input('intermediate-value', 'children')])
     
def update_dropdown_values(json_intermediate_data):    
    '''
    '''
    print('-------------------updating dropdown filters: Values-------------------')
    print(json_intermediate_data)
    df_final = pd.read_json(json_intermediate_data, orient='split')
    date_dict, values_date_default = dropdown_dict(df_final)
    return values_date_default

     
#-------------------------------------------------------- 
#Update graph based on filters
@app.callback(
    dash.dependencies.Output('graph-daily', 'figure'),
    [dash.dependencies.Input('date-dropdown', 'value'),
     dash.dependencies.Input('dataselector', 'value'),
     dash.dependencies.Input('intermediate-value', 'children')
     ,dash.dependencies.Input('adj-forecast-df', 'children')
     ])

def update_daily_viewfilters(selected_month, dataselected, json_intermediate_data, json_intermediate_adj):
    '''
    '''
    #json_intermediate_adj=None
    if json_intermediate_adj is not None:
        print("-------->>> adjusting forecast")
        df_final = pd.read_json(json_intermediate_adj, orient='split')
    else:
        df_final = pd.read_json(json_intermediate_data, orient='split')
        print("-------->>> using original forecast")
    
    
    #date_dict, values_date_default = dropdown_dict(df_final)
    filtered_df = df_final[df_final['Date'].dt.month.isin(selected_month)]
    traces = []
    month_list = []
    annotations=None
    for i in selected_month:
        month_list.append(calendar.month_abbr[i])
    
    if dataselected !=3: #Option 3 is Forecast Only!
        traces.append(go.Scatter(
                x=filtered_df[filtered_df['Volume']>0]['Date'],
                y=filtered_df[filtered_df['Volume']>0]['Volume'],
                mode='lines', name='Actuals'# for: '+",".join(month_list)
            ))
    if dataselected !=1: #Option 1 is Data Only!
        traces.append(go.Scatter(
            x=filtered_df[filtered_df['Forecast']>0]['Date'],
            y=filtered_df[filtered_df['Forecast']>0]['Forecast'],
            mode='lines', name='Forecast'# for: ' + ",".join(month_list)
          ))
        if 'Adj_Forecast' in filtered_df.columns:
            traces.append(go.Scatter(
                  x=filtered_df[filtered_df['Adj_Forecast']>0]['Date'],
                  y=filtered_df[filtered_df['Adj_Forecast']>0]['Adj_Forecast'],
                  mode='lines', name='Adj Forecast'# for: ' + ",".join(month_list)
        ))
            filter_annotes = filtered_df[filtered_df['Adj_Annotation']!='']
            annotations=[dict(
            x=filter_annotes['Date'].tolist()[i], y=0,#filter_annotes['Adj_Forecast'].tolist()[0],
            text=filter_annotes['Adj_Annotation'].tolist()[i], showarrow=True, arrowhead=7, 
            ax=0, ay=-20*(i+1)) for i in range(len(filter_annotes['Date'].tolist()))]
    
        if 'Forecast_upper' in filtered_df.columns:
            traces.append(go.Scatter(
                    x=filtered_df[filtered_df['Forecast']>0]['Date'].tolist() + filtered_df[filtered_df['Forecast']>0]['Date'].tolist()[::-1],
                    y=filtered_df[filtered_df['Forecast']>0]['Forecast_upper'].tolist() + filtered_df[filtered_df['Forecast']>0]['Forecast_lower'].tolist()[::-1],
                    fill='tozeroy', fillcolor='rgba(0,100,80,0.2)', line=dict(color='rgba(255,255,255,0)'), name='Forecast-errorzone'# for: ' + ",".join(month_list)
                    ))



    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'title': 'Months Selected: ' + ", ".join(month_list)},
            yaxis={'title': 'Volume'},
            #margin={'l': 40, 'b': 30, 't': 40, 'r': 0},
            #legend={'x': 0, 'y': 1},
            hovermode='closest',
            annotations=annotations
            #plot_bgcolor='#e0e0eb',
            #paper_bgcolor='#e0e0eb'
        )
    }
        

#-------------------------------------------------------- 
#Store the uploaded DF
@app.callback(dash.dependencies.Output('upload-data-df', 'children'),
              [dash.dependencies.Input('upload-data', 'contents'),
               dash.dependencies.Input('upload-data', 'filename'),
               dash.dependencies.Input('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
         children = [
             parse_contents(c, n, d)[1] for c, n, d in
             zip(list_of_contents, list_of_names, list_of_dates)]
         print(children[0])
         return children[0]

#-------------------------------------------------------- 
#Data Table Output
@app.callback(dash.dependencies.Output('output-data-upload', 'children'),
              [dash.dependencies.Input('upload-data', 'contents'),
               dash.dependencies.Input('upload-data', 'filename'),
               dash.dependencies.Input('upload-data', 'last_modified')])
def update_output_data(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
         children = [
             parse_contents(c, n, d)[0] for c, n, d in
             zip(list_of_contents, list_of_names, list_of_dates)]
         return children

#-------------------------------------------------------- 
#Forecast Adjustment Block
@app.callback(dash.dependencies.Output('adj-master-block-0', 'style'),
              [dash.dependencies.Input('adj-creator', 'n_clicks')],
              [dash.dependencies.State('adj-number', 'value')])
def update_adj_block0(creator_clicks, number_of_adj_blocks):
    if number_of_adj_blocks >= 1:
        return {'display': 'block', 'padding': '20 0'}
    else:
        return {'display': 'none'}

@app.callback(dash.dependencies.Output('adj-master-block-1', 'style'),
              [dash.dependencies.Input('adj-creator', 'n_clicks')],
              [dash.dependencies.State('adj-number', 'value')])
def update_adj_block1(creator_clicks, number_of_adj_blocks):
    if number_of_adj_blocks >=2:
        return {'display': 'block', 'padding': '20 0'}
    else:
        return {'display': 'none'}

@app.callback(dash.dependencies.Output('adj-master-block-2', 'style'),
              [dash.dependencies.Input('adj-creator', 'n_clicks')],
              [dash.dependencies.State('adj-number', 'value')])
def update_adj_block2(creator_clicks, number_of_adj_blocks):
    if number_of_adj_blocks >=3:
        return {'display': 'block', 'padding': '20 0'}
    else:
        return {'display': 'none'}
    
@app.callback(dash.dependencies.Output('adj-forecast', 'style'),
              [dash.dependencies.Input('adj-creator', 'n_clicks')],
              [dash.dependencies.State('adj-number', 'value')])
def update_adj_block_button(creator_clicks, number_of_adj_blocks):
    if number_of_adj_blocks >=1:
        return {'display': 'block', 'padding': '20 0'}
    else:
        return {'display': 'none'}



#----------------------------------------------------- 
#Forecast Adjuster
@app.callback(
    dash.dependencies.Output('adj-forecast-df', 'children'),
     [dash.dependencies.Input('intermediate-value', 'children'),
     dash.dependencies.Input('adj-forecast', 'n_clicks')],
     [dash.dependencies.State('adj-input-0', 'value'),
      dash.dependencies.State('datepicker-0', 'start_date'),
      dash.dependencies.State('datepicker-0', 'end_date'),
      dash.dependencies.State('adj-input-1', 'value'),
      dash.dependencies.State('datepicker-1', 'start_date'),
      dash.dependencies.State('datepicker-1', 'end_date'),
      dash.dependencies.State('adj-input-2', 'value'),
      dash.dependencies.State('datepicker-2', 'start_date'),
      dash.dependencies.State('datepicker-2', 'end_date')])
def adj_forecast(json_intermediate_data, n_clicks,
                 input0, stdt0, enddt0, 
                 input1, stdt1, enddt1, 
                 input2, stdt2, enddt2):
    '''
    '''
    print("--------->>> Entered forecast adjusting block")
    df_final = pd.read_json(json_intermediate_data, orient='split')
    #date_dict, values_date_default = dropdown_dict(df_final)
    filtered_df = df_final
    #clear existing columns
    if 'Adj_Forecast' in filtered_df.columns:
        filtered_df.drop('Adj_Forecast', axis=1)
    if 'Adj_Annotation' in filtered_df.columns:
        filtered_df.drop('Adj_Annotation', axis=1)
        
    if input0 is not None or input1 is not None or input2 is not None:
        filtered_df['Adj_Forecast'] = filtered_df['Forecast']
        filtered_df['Adj_Annotation'] = ''
        print(">>>>filtered_df processing...")
        print(filtered_df.tail())
        if stdt0 is not None and enddt0 is not None:
            print("-->>-->>-->> processing 1st adjustment")
            filtered_df['Adj_Forecast'][(filtered_df['Date']>=stdt0) & (filtered_df['Date'] <=enddt0)] = filtered_df['Adj_Forecast'][(filtered_df['Date']>=stdt0) & (filtered_df['Date'] <=enddt0)] + float(input0)
            filtered_df['Adj_Annotation'][filtered_df['Date']==stdt0] = "Adj. #1 Applied from:\n" + str(stdt0) + " to " + str(enddt0)
        if stdt1 is not None and enddt1 is not None:
            print("-->>-->>-->> processing 2nd adjustment")
            filtered_df['Adj_Forecast'][(filtered_df['Date']>=stdt1) & (filtered_df['Date'] <=enddt1)] = filtered_df['Adj_Forecast'][(filtered_df['Date']>=stdt1) & (filtered_df['Date'] <=enddt1)] + float(input1)
            filtered_df['Adj_Annotation'][filtered_df['Date']==stdt1] = "Adj. #2 Applied from:\n" + str(stdt1) + " to " + str(enddt1)
        if stdt2 is not None and enddt2 is not None:
            print("-->>-->>-->> processing 3rd adjustment")
            filtered_df['Adj_Forecast'][(filtered_df['Date']>=stdt2) & (filtered_df['Date'] <=enddt2)] = filtered_df['Adj_Forecast'][(filtered_df['Date']>=stdt2) & (filtered_df['Date'] <=enddt2)] + float(input2)
            filtered_df['Adj_Annotation'][filtered_df['Date']==stdt2] = "Adj. #3 Applied from:\n" + str(stdt2) + " to " + str(enddt2)
        print("--------->>> after forecast adjustment")
    print(filtered_df.tail())
    return filtered_df.to_json(date_format='iso', orient='split')


app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})


if __name__ == '__main__':
    app.run_server(debug=True)