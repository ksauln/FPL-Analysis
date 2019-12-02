#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Started on Mon Nov 11 11:04:09 2019

@author: Kyle Sauln


Uses data from:
    https://github.com/vaastav/Fantasy-Premier-League/tree/master/data

and elements of building out the season from:
    https://github.com/solpaul/fpl-prediction
"""
''' 

Enter this most recent Game week. Helps build the 2019-2020 season
Make sure to get most recent data from here:
    
    https://github.com/vaastav/Fantasy-Premier-League/tree/master/data
    
     
'''
current_gw = 13
current_season =1920

#set working directory
#import os
#os.chdir("/Users/Sauln/Documents/Coding/Python/FPL/NEW")

# First Import data
# required libriaries
from pathlib import Path
from build_out import *
import pandas as pd

# path to data directory
path = Path('/Users/Sauln/Documents/Coding/Python/FPL/NEW/data')

# paths to each season's data
season_paths = [path/'2016-17', path/'2017-18', path/'2018-19',path/'2019-20']

# names for each season
season_names = ['1617', '1718', '1819', '1920']

# team codes
teams = pd.read_csv(path/'teams.csv')

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
df_train.to_csv(path/'initial_train.csv')

## now need to create the prediction set
# start by running fixtures from build_out

fixtures = remaining_fixtures(path/'2019-20/fixtures.csv', current_gw, current_season, teams)

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
next_5 = next_n_fixtures (fixtures, next_n_games=5, current_gw=12)

   
