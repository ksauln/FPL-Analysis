#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 10:56:51 2019

@author: Sauln

Uses data from:
    https://github.com/vaastav/Fantasy-Premier-League/tree/master/data

and elements of building out the season from:
    https://github.com/solpaul/fpl-prediction

Make sure to get the most recent data after games are played from vaastav's repository


NOTE: This app is combines the build_out.py, FPL_Analysis.py, and FPL_Dashboard.py
       files that I use for development and to run locally.
       Need to remember to uncomment the server when pushing to heroku
"""
# Enter Current Game Week and Seaon.
# Will need to update the program every year to point to the correct season.
# Need to update every "week" to make sure everything is up to date

current_gw = 17
current_season =1920


##########################################################################################
##########################################################################################
#                               First build functions                                    #
##########################################################################################
##########################################################################################


import pandas as pd
import numpy as np
import requests



def build_players(path, season_paths, season_names, teams):
    # read in player information for each season and add to list
    season_players = []

    for season_path in season_paths:
        players = pd.read_csv(season_path + '/players_raw.csv',
                               usecols=['first_name', 'second_name', 'id',
                                        'team_code', 'element_type', 'now_cost',
                                        'chance_of_playing_next_round'], encoding='latin1')
        season_players.append(players)

    if len(season_players) > 1:
        # two danny wards in 1819, rename the new one
        season_players[2].loc[143, 'second_name'] = 'Ward_2'

    # create full name field for each player
    for players in season_players:
        players['full_name'] = players['first_name'] + '_' + players['second_name']
        players.drop(['first_name', 'second_name'], axis=1, inplace=True)

    # create series of all unique player names
    all_players = pd.concat(season_players, axis=0, ignore_index=True, sort=False)
    all_players = pd.DataFrame(all_players['full_name'].drop_duplicates())

    # create player dataset with their id, team code and position id for each season
    for players, season in zip(season_players, season_names):
        all_players = all_players.merge(players, on='full_name', how='left')
        all_players.rename(index=str,
                           columns={'id':'id_' + season,
                                    'team_code':'team_' + season,
                                    'element_type': 'position_' + season,
                                    'now_cost': 'cost_' + season,
                                    'chance_of_playing_next_round': 'play_proba_' + season},
                           inplace=True)

    return all_players


# function to create season training dataset
# each player has a row for each gameweek
def build_season(path, season, all_players, teams, gw):

    # season specific list and strings to use for merging
    df_season = []
    id_season = 'id_' + season
    id_team = 'team_' + season
    id_position = 'position_' + season

    # read in each gameweek and append to season list
    for i in gw:
        gw = '/gws/gw' + str(i) + '.csv'
        gw_df = pd.read_csv(path + gw, encoding='latin1')
        gw_df['gw'] = i
        df_season.append(gw_df)

    # concatenate entire season
    df_season = pd.concat(df_season, axis=0)

    # join to player, team and team market value datasets to create season training set
    df_season = df_season.merge(all_players, left_on='element', right_on=id_season, how='left')
    df_season = df_season.merge(teams, left_on='opponent_team', right_on=id_team, how='left')
    df_season = df_season.merge(teams, left_on=id_team + '_x', right_on='team_code', how='left')
    '''
    df_season = df_season.merge(teams_mv[teams_mv['season'] == season],
                                left_on='team_x', right_on='name', how='left')
    df_season = df_season.merge(teams_mv[teams_mv['season'] == season],
                                left_on='team_y', right_on='name', how='left')
    '''
    df_season = df_season[['full_name', 'gw',
                           id_position, 'minutes', 'team_y',
                           'team_x', 'was_home', 'total_points',
                           'assists',
                            'bonus', 'bps','clean_sheets', 'creativity',
                            'element','fixture','goals_conceded',
                            'goals_scored','ict_index','influence',
                            'kickoff_time', 'own_goals', 'penalties_missed',
                            'penalties_saved','red_cards',
                            'saves', 'selected','team_a_score',
                            'team_h_score', 'threat','transfers_balance',
                            'transfers_in','transfers_out','value',
                            'yellow_cards' ]]


    df_season.columns = ['player', 'gw',
                          'position', 'minutes', 'team',
                          'opponent_team', 'was_home', 'total_points',
                          'assists',
                            'bonus', 'bps','clean_sheets', 'creativity',
                            'element','fixture','goals_conceded',
                            'goals_scored','ict_index','influence',
                            'kickoff_time', 'own_goals', 'penalties_missed',
                            'penalties_saved','red_cards',
                            'saves', 'selected','team_a_score',
                            'team_h_score', 'threat','transfers_balance',
                            'transfers_in','transfers_out','value',
                            'yellow_cards' ]
    df_season['season'] = season
    df_season['position'] = df_season['position'].astype(int)

    return df_season

#function for remaining fixtures
def remaining_fixtures(curr_fixtures,current_gw, current_season, teams):
    # set starting gameweek (where are we right now in the season)
    fixtures = pd.read_csv(curr_fixtures)

    #change a few column names
    fixtures.rename(columns ={ 'event':'gw',
                               'team_a':'away_team',
                               'team_h':'home_team'
                            }, inplace=True)

    fixtures = fixtures[fixtures['gw'] >= current_gw]

    #convert team_a and team_h to type object add team name
    #fixtures['away_team'] = fixtures['away_team'].apply(lambda x: str(x))
    #fixtures['home_team'] = fixtures['home_team'].apply(lambda x: str(x))

    # add team codes for home and away teams

    fixtures = fixtures.merge(teams, left_on='home_team', right_on='team_'+ str(current_season), how='left')
    fixtures = fixtures.merge(teams, left_on='away_team', right_on='team_'+ str(current_season), how='left')
    fixtures = fixtures[['gw', 'team_x', 'team_y', 'team_code_x','team_h_difficulty', 'team_code_y','team_a_difficulty']]
    fixtures.rename(index=str,
                    columns={'team_x':'home_team',
                             'team_y':'away_team',
                             'team_code_x':'home_team_code',
                             'team_h_difficulty':'home_team_diff',
                             'team_code_y':'away_team_code',
                             'team_a_difficulty':'away_team_diff'},
                    inplace=True)
    return fixtures


#function for the remaining season
def remaining_season_func(all_players, current_season, fixtures, path):
    # join home team to all players for current season
    home_df = fixtures.merge(all_players,
                   left_on='home_team_code',
                   right_on='team_'+ str(current_season),
                   how='left')

    # pull out the required fields and rename columns
    home_df = home_df[['gw', 'home_team', 'away_team', 'full_name', 'position_1920', 'cost_1920', 'play_proba_1920']]
    home_df.rename(index=str,
                   columns={'home_team':'team',
                            'away_team':'opponent_team',
                            'full_name':'player',
                            'position_1920':'position',
                            'cost_1920':'price',
                            'play_proba_1920':'play_proba'},
                  inplace=True)

    # add home flag
    home_df['was_home'] = True

    # join away team to all players for current season
    away_df = fixtures.merge(all_players,
                   left_on='away_team_code',
                   right_on='team_'+ str(current_season),
                   how='left')

    # pull out the required fields and rename columns
    away_df = away_df[['gw',  'away_team', 'home_team', 'full_name', 'position_1920', 'cost_1920', 'play_proba_1920']]
    away_df.rename(index=str,
                   columns={'away_team':'team',
                            'home_team':'opponent_team',
                            'full_name':'player',
                            'position_1920':'position',
                            'cost_1920':'price',
                            'play_proba_1920':'play_proba'},
                  inplace=True)

    # add home flag
    away_df['was_home'] = False

    # concatenate home and away players
    remaining_season_df = home_df.append(away_df).reset_index(drop=True)

    # add season name
    remaining_season_df['season'] = '1920'

    # divide cost by 10 for actual cost
    remaining_season_df['price'] = remaining_season_df['price']/10

    # set availability probability
    # 0 = 0% chance, 25 = 25% chance, etc
    # 'None' or '100' = 100% chance
    remaining_season_df.loc[remaining_season_df['play_proba'] == 'None', 'play_proba'] = 100
    remaining_season_df['play_proba'] = remaining_season_df['play_proba'].astype('float') / 100

    # set minutes equal to 90 multiplied by their play probabiliby for all players, for now
    remaining_season_df['minutes'] = 90 * remaining_season_df['play_proba']

    # cast position to integer
    remaining_season_df['position'] = remaining_season_df['position'].astype(int)

    # save latest prediction set to csv for local use
    #remaining_season_df.to_csv(path + 'remaining_season.csv')

    return remaining_season_df


#function to create the next 5 fixtures and their difficulty

def next_n_fixtures(fixtures, next_n_games, current_gw):
    # create schedule df

    #get all home fixtures
    schedule1 = fixtures.copy()
    schedule1['was_home'] =True
    schedule1.rename(index=str,
                    columns={ 'home_team':'team',
                              'home_team_code':'team_code',
                              'home_team_diff':'team_diff',
                              'away_team':'opponent_team',
                              'away_team_code': 'opponent_team_code',
                              'away_team_diff':'opponent_team_diff'},
                              inplace=True)

    #get awal fixtures
    schedule2 = fixtures.copy()
    schedule2['was_home'] =False
    schedule2.rename(index=str,
                    columns={ 'away_team':'team',
                              'away_team_code':'team_code',
                              'away_team_diff':'team_diff',
                              'home_team':'opponent_team',
                              'home_team_code': 'opponent_team_code',
                              'home_team_diff':'opponent_team_diff'},
                              inplace=True)

    #combine home and away
    schedule_df = schedule1.append(schedule2).sort_values(by=['team_code','gw']).reset_index(drop=True)
    #rearrage columns
    schedule_df = schedule_df[['gw','team', 'team_code','team_diff',
                           'opponent_team','opponent_team_code','opponent_team_diff',
                           'was_home']]

    dic = {}

    for team_code in schedule_df['team_code'].unique():
        #schedule_sort=schedule_df.sort_values(by=[team_code,'gw'])
        team_looking_at = schedule_df.loc[schedule_df['team_code'] ==team_code]
        next_n= team_looking_at[(team_looking_at['gw'] >= current_gw +1) & (team_looking_at['gw'] <= current_gw +next_n_games)]
        dic[team_code] = next_n

    return dic

##########################################################################################
##########################################################################################
#                           Second Run analysis                                          #
##########################################################################################
##########################################################################################

#current_gw = 13
#current_season =1920

# path to data in github repo
path = 'data/'

# paths to each season's data
season_paths = [path + '2016-17', path + '2017-18', path + '2018-19',path + '2019-20']

# names for each season
season_names = ['1617', '1718', '1819', '1920']

# team codes
teams = pd.read_csv(path + 'teams.csv')

all_players = build_players(path, season_paths, season_names, teams)

# create training sets for each season minus the teams values because for some reason
# 2019-2020 isnt working add in ",teams_mv" to the end
df_1617 = build_season(season_paths[0], season_names[0], all_players, teams, range(1, 39))
df_1718 = build_season(season_paths[1], season_names[1], all_players, teams, range(1, 39))
df_1819 = build_season(season_paths[2], season_names[2], all_players, teams, range(1, 39))
df_1920 = build_season(season_paths[3], season_names[3], all_players, teams, range(1, current_gw))

# size of each season
[x.shape for x in [df_1617, df_1718, df_1819, df_1920]]

# join together into one dataframe
df_train = pd.concat([df_1617, df_1718, df_1819], ignore_index=True, axis=0)

df_train.shape

# save latest training set to csv
# for local use
#df_train.to_csv(path/'initial_train.csv')

## now need to create the prediction set
# start by running fixtures from build_out

fixtures = remaining_fixtures(path+ '2019-20/fixtures.csv', current_gw, current_season, teams)

#now get the remaining season left for the players
remaining_season = remaining_season_func(all_players, current_season, fixtures, path)

'''
Create averages for the players up to the current game week
'''
#get list of current players
players_current = all_players[all_players['team_'+ str(current_season)] > 0 ]
players_current = players_current[['full_name',
                                   'play_proba_'+str(current_season),
                                   'position_'+str(current_season),
                                   'id_'+str(current_season),
                                   'cost_'+str(current_season),
                                   'team_'+str(current_season)]]

totals_curr = df_1920.groupby(['player']).sum().reset_index()
means_curr = df_1920.groupby(['player']).mean().reset_index()


# get next 5 fixtures
next_5 = next_n_fixtures (fixtures, next_n_games=5, current_gw=current_gw)


##########################################################################################
##########################################################################################
#                           Last set up app                                              #
##########################################################################################
##########################################################################################



# imports for plotly and dash
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import dash_auth
import dash_bootstrap_components as dbc


#creating username and password set to log into app

USERNAME_PASSWORD_PAIRS =[['user','view2019']]




app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.GRID],
                meta_tags=[
                            {
                                "name": "fplanalysis",
                                "content": "width=device-width, initial-scale=1, maximum-scale=1.0, user-scalable=no",
                            }
                        ]
                )


# UNCOMMENT WHEN PUSHING TO HEROKU
auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)
server=app.server

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

def build_bar_graph1():
    return html.Div(
            className="bar graph1",
            children=[
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
                    ],
                )

def build_bar_graph2():
    return html.Div(
            className="bar graph2",
            children=[
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
                html.Div(
                className="upcoming_fixtures",
                children=[
                        html.Div(
                                dbc.Container([
                                        dbc.Row(
                                            [
                                                dbc.Col(dcc.Graph(id="next_fixtures_p1")),
                                                dbc.Col(dcc.Graph(id="next_fixtures_p2"))
                                            ]
                                                )
                                            ])
                                ),
                        ],
                        )
                    ]
                )



app.layout = html.Div(
        dbc.Container([
            dbc.Row(html.H1("FPL Analytics"),
                        style={"font-size":18}),
            dbc.Row(
                [
                    dbc.Col(build_player_selection(), width=4,align="start")
                ]
                    ),
            dbc.Row(html.H2("Bar Graph Comparsion"),
                        style={"font-size":12}),
            dbc.Row(
                [
                        dbc.Col(build_bar_graph1(),width=6),
                        dbc.Col(build_bar_graph2(),width=6)
                ]),
            dbc.Row(html.H2("Trending Graph"),
                        style={"font-size":12}),
            dbc.Row(
                    dbc.Col(build_trend_graphs())
                    ),
            dbc.Row(html.H2("Upcoming Fixtures"),
                    style={"font-size":12}),
            dbc.Row(
                    dbc.Col(build_upcoming_fixtures())
                    )
            
                ])
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

def update_next5_p2(player1):
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

def update_next5_p2(player2):
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
