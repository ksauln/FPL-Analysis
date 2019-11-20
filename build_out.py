# helpers.py
import pandas as pd
import numpy as np
import requests
import lxml.html as lh


def build_players(path, season_paths, season_names, teams):
    # read in player information for each season and add to list
    season_players = []

    for season_path in season_paths:
        players = pd.read_csv(season_path/'players_raw.csv',
                               usecols=['first_name', 'second_name', 'id',
                                        'team_code', 'element_type', 'now_cost',
                                        'chance_of_playing_next_round'])
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
        gw = 'gws/gw' + str(i) + '.csv'
        gw_df = pd.read_csv(path/gw, encoding='latin')
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

    # save latest prediction set to csv
    remaining_season_df.to_csv(path/'remaining_season.csv')

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