#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 10:56:51 2019

@author: Sauln
"""

# runs required steps to get data
from FPL_Analysis import *

# imports for plotly and dash
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import dash_auth


#creating username and password set to log into app

USERNAME_PASSWORD_PAIRS =[['user','view2019']]




external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, 
                external_stylesheets=external_stylesheets,
                meta_tags=[
                            {
                                "name": "fplanalysis",
                                "content": "width=device-width, initial-scale=1, maximum-scale=1.0, user-scalable=no",
                            }
                        ]
                )

#enable authorization

auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)
#server=app.server

# Selectable options for graphs
available_players = totals_curr['player'].unique()
available_metric1 = list(['minutes','total_points','assists','bonus','bps','goals_conceded',
                          'goals_scored','own_goals','penalties_missed',
                          'penalities_saved','red_cards','saves','yellow_cards'])
available_metric2 = list(['minutes','total_points','assists','bonus','bps','goals_conceded',
                          'goals_scored','own_goals','penalties_missed',
                          'penalities_saved','red_cards','saves','yellow_cards'])
available_trend_metric = list(['minutes','total_points','assists','bonus','bps','goals_conceded',
                          'goals_scored','own_goals','penalties_missed',
                          'penalities_saved','red_cards','saves','yellow_cards','clean_sheets',
                          'selected'])


###############################################################
# Create Sections
def build_player_selection():
    return html.Div(
            id="upper-left",
            className="player selection",
            children=[
                    html.P(
                            className="section-title",
                            children="Choose the players you want to compare",
                            ),
                html.Div(
                className="control-row-1",
                children=[
                    html.Div(
                        id="select-player1",
                        children=[
                            html.Label("Select first player"),
                            dcc.Dropdown(
                                id="player1",
                                options=[{"label": i, "value": i} for i in available_players],
                                value=available_players[1],
                            ),
                        ],style={'width':'70%'}
                    ),
                    html.Div(
                        id="select-player2",
                        children=[
                            html.Label("Select second player"),
                            dcc.Dropdown(
                                id="player2",
                                options=[{"label": i, "value": i} for i in available_players],
                                value=available_players[2],
                                        ),
                                    ],style={'width':'70%'}
                                ),
                            ],
                        ),
                    ],  
                )

def build_bar_graphs():
    return html.Div(
            id="upper-right",
            className="bar graphs",
            children=[
                    html.P(
                            className="section-title",
                            children="Graph Comparsion",
                            ),
                html.Div(
                className="totals",
                children=[
                    html.Div(
                        id="select-metric1",
                        children=[
                            html.Label("Select totals metric to compare"),
                            dcc.Dropdown(
                                id="metric1",
                                options=[{"label": i, "value": i} for i in available_metric1],
                                value=available_metric1[1],
                                        ),
                            dcc.Graph(id='player_tot_graph'),
                                    ],
                                ),
                           ],
                          ),
                 html.Div(
                className="averages",
                children=[
                    html.Div(
                        id="select-metric2",
                        children=[
                            html.Label("Select averages metric to compare"),
                            dcc.Dropdown(
                                id="metric2",
                                options=[{"label": i, "value": i} for i in available_metric2],
                                value=available_metric2[1],
                                        ),
                            dcc.Graph(id='player_avg_graph'),
                                    ],
                                ),
                           ],
                          ),
                    ],
                )


def build_trend_graphs():
    return html.Div(
            id="middle",
            className="trend graphs",
            children=[
                    html.P(
                            className="section-title",
                            children="Trending",
                            ),
                html.Div(
                className="trend",
                children=[
                    html.Div(
                        id="select-trend",
                        children=[
                            html.Label("Select metric to look at"),
                            dcc.Dropdown(
                                id="trend_metric",
                                options=[{"label": i, "value": i} for i in available_trend_metric],
                                value=available_metric1[1],
                                        ),
                            dcc.Graph(id='trend_graph'),
                                    ],
                                ),
                           ],
                          ),
                    ],
                )

def build_upcoming_fixtures():
    return html.Div(
            id="bottom",
            className="upcoming",
            children=[
                    html.P(
                            className="section-title",
                            children="Upcoming Fixtures",
                            ),
                html.Div(
                className="upcoming_fixtures",
                children=[
                        html.Div([
                                    dcc.Graph(id="next_fixtures_p1")
                                ],
                                className="row",
                                    style={'width': '50%', 'display': 'inline-block'}),
                        html.Div([
                                    dcc.Graph(id="next_fixtures_p2")
                                ],
                                className="row",
                                    style={'width': '50%', 'display': 'inline-block'})
                                ],
                            ),
                    ],
                )



app.layout = html.Div(
    className="container scalable",
    children=[
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.H6("FPL Analytics"),
            ],
        ),
        html.Div(
            id="left-container",
            className="row",
            children=[
                build_player_selection()
                    ],style={'width':'40%','display':'inline-block'}
                ),
        html.Div(
                id="right-container",
                children=[
                        build_bar_graphs()
                        ],style={'width':'60%','display':'inline-block'}
                    ),
         html.Div(
                id="middle-container",
                children=[
                        build_trend_graphs()
                        ],
                    ),
         html.Div(
                 id="bottom-container",
                 children =[
                         build_upcoming_fixtures()
                         ],
                 ),
        ],
    )
      

###############################################################
# Call back for TOTALS Bar Graph
@app.callback(
    Output('player_tot_graph', 'figure'),
    [Input('player1', 'value'),
     Input('player2', 'value'),
     Input('metric1','value')])


def update_player_tot_graph(player1,player2, metric1):
    trace1 = go.Bar(x= totals_curr[totals_curr['player'] == player1]['player'],
                    y= totals_curr[totals_curr['player'] == player1][metric1],
                    name =player1)
    trace2 = go.Bar(x= totals_curr[totals_curr['player'] == player2]['player'],
                    y= totals_curr[totals_curr['player'] == player2][metric1],
                    name =player2)

    return {
        'data': [trace1,trace2],

        'layout': go.Layout(
                title= metric1,
                barmode="group"
        )
    }
###############################################################
# Call back for AVG Bar Graph
@app.callback(
    Output('player_avg_graph', 'figure'),
    [Input('player1', 'value'),
     Input('player2', 'value'),
     Input('metric2','value')])


def update_player_avg_graph(player1,player2, metric2):
    trace1 = go.Bar(x= means_curr[means_curr['player'] == player1]['player'],
                    y= means_curr[means_curr['player'] == player1][metric2],
                    name =player1)
    trace2 = go.Bar(x= means_curr[means_curr['player'] == player2]['player'],
                    y= means_curr[means_curr['player'] == player2][metric2],
                    name =player2)

    return {
        'data': [trace1,trace2],

        'layout': go.Layout(
                title= "Average " + metric2 + " Per Game",
                barmode="group"
        )
    }
###############################################################
# Call back for Trend Graph
@app.callback(
    Output('trend_graph', 'figure'),
    [Input('player1', 'value'),
     Input('player2', 'value'),
     Input('trend_metric','value')])

def update_trend_graph(player1,player2, trend_metric):
    trace1 = go.Scatter(x= df_1920[df_1920['player'] == player1]['gw'],
                    y= df_1920[df_1920['player'] == player1][trend_metric],
                    name =player1,
                    mode='lines+markers')

    trace2 = go.Scatter(x= df_1920[df_1920['player'] == player2]['gw'],
                y= df_1920[df_1920['player'] == player2][trend_metric],
                name =player2,
                mode='lines+markers')

    return {
        'data': [trace1, trace2],

        'layout': go.Layout(
                title=trend_metric + " Over Season",
                yaxis={"title":trend_metric},
                xaxis={"title":"Game Week"}
        )
    }
###############################################################
# Call back for next 5 fixtures
@app.callback(
    Output("next_fixtures_p1", "figure"),
     [Input('player1', 'value')])

def update_graph(player1):
    value_header = ['Game Week','Opponent','Difficulty','Home or Away']

    #create dataframe with the stats we want to look at
    #Player1 info
    #pull out team number
    p1_team = players_current.loc[(players_current['full_name']==player1),'team_1920'].values[0]
    #pull out that team from the next5 dictionary

    p1_next5 = next_5[p1_team][['gw','opponent_team','opponent_team_diff','was_home']]

    #convert true/fase to home/away
    home_away = {True:'Home',
                 False: 'Away'
                 }
    p1_next5['was_home'] = p1_next5['was_home'].map(home_away)

    #create value_Cell
    value_cell = [p1_next5['gw'],p1_next5['opponent_team'],
                  p1_next5['opponent_team_diff'],p1_next5['was_home']]

    trace = go.Table(
        header={"values": value_header, "fill": {"color": "LightSkyBlue"}, "align": ['center'], "height": 35,
                "line": {"width": 2, "color": "#685000"}, "font": {"size": 15}},
        cells={"values": value_cell, "fill": {"color": "LightSkyBlue"}, "align": ['left', 'center'],
               "line": {"color": "#685000"}})

    layout = go.Layout(title=player1 + " Upcoming Fixtures", height=600)


    return {
            "data": [trace],
            "layout": layout
            }

@app.callback(
    Output("next_fixtures_p2", "figure"),
     [Input('player2', 'value')])

def update_graph(player2):
    value_header = ['Game Week','Opponent','Difficulty','Home or Away']

    #create dataframe with the stats we want to look at
    #Player1 info
    #pull out team number
    p2_team = players_current.loc[(players_current['full_name']==player2),'team_1920'].values[0]
    #pull out that team from the next5 dictionary

    p2_next5 = next_5[p2_team][['gw','opponent_team','opponent_team_diff','was_home']]

    #convert true/fase to home/away
    home_away = {True:'Home',
                 False: 'Away'
                 }
    p2_next5['was_home'] = p2_next5['was_home'].map(home_away)

    #create value_Cell
    value_cell = [p2_next5['gw'],p2_next5['opponent_team'],
                  p2_next5['opponent_team_diff'],p2_next5['was_home']]

    trace = go.Table(
        header={"values": value_header, "fill": {"color": "LightSkyBlue"}, "align": ['center'], "height": 35,
                "line": {"width": 2, "color": "#685000"}, "font": {"size": 15}},
        cells={"values": value_cell, "fill": {"color": "LightSkyBlue"}, "align": ['left', 'center'],
               "line": {"color": "#685000"}})

    layout = go.Layout(title=player2 + " Upcoming Fixtures", height=600)


    return {
            "data": [trace],
            "layout": layout
            }
###############################################################
if __name__ == '__main__':
    app.run_server()
