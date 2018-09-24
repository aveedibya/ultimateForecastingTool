# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 13:56:20 2018

@author: agarw
"""

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt

def add_adj_block(number_of_adj):
    '''
    '''
    adj_block = []
    dash_dependencies_Input = []
    for i in range(number_of_adj-1):
        one_adj_block(adj_block, adj_block_number=i, final_adj_block=0)
        dash_dependencies_Input.append(dash.dependencies.Input('adj-input-' + str(int(i)), 'value'))
    one_adj_block(adj_block, adj_block_number=i+1, final_adj_block=1)  
    dash_dependencies_Input.append(dash.dependencies.Input('adj-input-' + str(int(i+1)), 'value'))
    return adj_block, dash_dependencies_Input

def one_adj_block(listadjelements, adj_block_number=0, final_adj_block=1):
    '''
    '''
    print('----->>> creating adj block number' + str(adj_block_number))
    if final_adj_block == 1:
        listadjelements.append(
                html.Div(children=[html.Label('Forecast Adj-' + str(int(adj_block_number+1))),
                            dcc.DatePickerRange(id = 'datepicker-'  + str(int(adj_block_number)),
                            start_date_placeholder_text="Start Period",
                            end_date_placeholder_text="End Period",
                            calendar_orientation='horizontal',
                            clearable=True,
                            with_portal=True,
                            start_date=dt.now()),
                          dcc.Input(id='adj-input-' + str(int(adj_block_number)), type='text'),
                          ], id='adj-master-block-' + str(int(adj_block_number)), style={'display': 'none', 'fontSize': '8'})
        )
        listadjelements.append(html.Button('Adj Forecast', id='adj-forecast', style={'display': 'none'}))
    else:
        listadjelements.append(
                html.Div(children=[html.Label('Forecast Adj-' + str(int(adj_block_number+1))),
                          dcc.DatePickerRange(id = 'datepicker-'  + str(int(adj_block_number)),
                            start_date_placeholder_text="Start Period",
                            end_date_placeholder_text="End Period",
                            calendar_orientation='horizontal',
                            clearable=True,
                            with_portal=True,
                            start_date=dt.now()),
                          dcc.Input(id='adj-input-' + str(int(adj_block_number)), type='text'),
                          ], id='adj-master-block-' + str(int(adj_block_number)), style={'display': 'none', 'fontSize': '8px'})
        )
    
    return listadjelements