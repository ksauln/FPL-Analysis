#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 20:03:48 2019

@author: Sauln
"""

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

app = dash.Dash()

available_players = totals_curr['player'].unique()

app.layout = html.Div([

   # Div for Player selection, labeled as player1 and player2
        html.Div([
            dcc.Dropdown(
                id='player1',
                options=[{'label': i, 'value': i } for i in available_players],
                value='Jamie_Vardy'
                        ),
                    ],
                    style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='player2',
                options=[{'label': i, 'value': i} for i in available_players],
                value='James_Maddison'
                        )
                ],
                style={'width': '48%', 'display': 'inline-block'}),

# Divs for Total Points Bar Graph
         html.Div([
                dcc.Graph(id='player_tot_pts')
                ],
                style={'width': '48%', 'display': 'inline-block'}),

#Div for Average Points Bar Graph
          html.Div([
                dcc.Graph(id='player_avg_pts')
                ],
                style={'width': '48%', 'display': 'inline-block'}),


  # scatterplot of current points
        html.Div([
                dcc.Graph(id='points_over_season')
                ],
                    ),

# Insert Table for statistics
        html.Div([
                dcc.Graph(id="other_stats")
                ],
                className="row",
                style={"padding": 20}),


# Insert table for next 5 fixtures
        html.Div([
                dcc.Graph(id="next_fixtures_p1")
                ],
                className="row",
                style={"padding": 20,'width': '48%', 'display': 'inline-block'}),
        html.Div([
                dcc.Graph(id="next_fixtures_p2")
                ],
                className="row",
                style={"padding": 20,'width': '48%', 'display': 'inline-block'}),


    ])


# Call back for total points Bar Graph
@app.callback(
    Output('player_tot_pts', 'figure'),
    [Input('player1', 'value'),
     Input('player2', 'value')])


def update_player_tot_pts(player1,player2):
    trace1 = go.Bar(x= totals_curr[totals_curr['player'] == player1]['player'],
                    y= totals_curr[totals_curr['player'] == player1]['total_points'],
                    name =player1)
    trace2 = go.Bar(x= totals_curr[totals_curr['player'] == player2]['player'],
                    y= totals_curr[totals_curr['player'] == player2]['total_points'],
                    name =player2)

    return {
        'data': [trace1,trace2],

        'layout': go.Layout(
                title= " Total Points",
                barmode="group"
        )
    }

# Call back for total points Bar Graph
@app.callback(
    Output('player_avg_pts', 'figure'),
    [Input('player1', 'value'),
     Input('player2', 'value')])


def update_player_avg_pts(player1,player2):
    trace1 = go.Bar(x= means_curr[means_curr['player'] == player1]['player'],
                    y= means_curr[means_curr['player'] == player1]['total_points'],
                    name =player1)
    trace2 = go.Bar(x= means_curr[means_curr['player'] == player2]['player'],
                    y= means_curr[means_curr['player'] == player2]['total_points'],
                    name =player2)

    return {
        'data': [trace1,trace2],

        'layout': go.Layout(
                title= "Avg Points Per Game",
                barmode="group"
        )
    }


# Call back for points over season

@app.callback(
    Output('points_over_season', 'figure'),
    [Input('player1', 'value'),
     Input('player2', 'value')])

def update_points_over_season(player1,player2):
    trace1 = go.Scatter(x= df_1920[df_1920['player'] == player1]['gw'],
                    y= df_1920[df_1920['player'] == player1]['total_points'],
                    name =player1,
                    mode='lines+markers')

    trace2 = go.Scatter(x= df_1920[df_1920['player'] == player2]['gw'],
                y= df_1920[df_1920['player'] == player2]['total_points'],
                name =player2,
                mode='lines+markers')

    return {
        'data': [trace1, trace2],

        'layout': go.Layout(
                title="Game Week Points",
                yaxis={"title":"Points"},
                xaxis={"title":"Game Week"}
        )
    }



# Call back for stats table
@app.callback(
    Output("other_stats", "figure"),
     [Input('player1', 'value'),
     Input('player2', 'value')])


def update_graph(player1, player2):
    value_header = ['Category',player1, player2]

    #create dataframe with the stats we want to look at
    #Player1 info
    p1_df = pd.DataFrame([['Goals Scored',totals_curr.loc[(totals_curr['player']==player1),'goals_scored'].values[0]],
                          ['Total Points',totals_curr.loc[(totals_curr['player']==player1),'total_points'].values[0]],
                          ['Total Assists',totals_curr.loc[(totals_curr['player']==player1),'assists'].values[0]]
                         ],
            columns=['Category',player1])

    #Player2 Info
    p2_df = pd.DataFrame([['Goals Scored',totals_curr.loc[(totals_curr['player']==player2),'goals_scored'].values[0]],
                      ['Total Points',totals_curr.loc[(totals_curr['player']==player2),'total_points'].values[0]],
                      ['Total Assists',totals_curr.loc[(totals_curr['player']==player2),'assists'].values[0]]
                     ],
        columns=['Category',player2])

    #Combine to create table
    player_stats = p1_df.merge(p2_df, left_on='Category', right_on='Category', how='left')

    #create value_Cell
    value_cell = [player_stats['Category'],player_stats[player1],player_stats[player2]]

    trace = go.Table(
        header={"values": value_header, "fill": {"color": "#FFD957"}, "align": ['center'], "height": 35,
                "line": {"width": 2, "color": "#685000"}, "font": {"size": 15}},
        cells={"values": value_cell, "fill": {"color": "#FFE89A"}, "align": ['left', 'center'],
               "line": {"color": "#685000"}})

    layout = go.Layout(title=f"Player Stats", height=600)


    return {
            "data": [trace],
            "layout": layout
            }

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
        header={"values": value_header, "fill": {"color": "#FFD957"}, "align": ['center'], "height": 35,
                "line": {"width": 2, "color": "#685000"}, "font": {"size": 15}},
        cells={"values": value_cell, "fill": {"color": "#FFE89A"}, "align": ['left', 'center'],
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
        header={"values": value_header, "fill": {"color": "#FFD957"}, "align": ['center'], "height": 35,
                "line": {"width": 2, "color": "#685000"}, "font": {"size": 15}},
        cells={"values": value_cell, "fill": {"color": "#FFE89A"}, "align": ['left', 'center'],
               "line": {"color": "#685000"}})

    layout = go.Layout(title=player2 + " Upcoming Fixtures", height=600)


    return {
            "data": [trace],
            "layout": layout
            }


if __name__ == '__main__':
    app.run_server()
