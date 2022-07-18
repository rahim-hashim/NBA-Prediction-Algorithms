import os
import sys
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import Rectangle, Patch

from fuzzy_lookup import fuzzy_matching_df
from stat_info import STAT_LIST, stat_dict, stat_precision, stat_range
from plot_helper.plot_matchups import plot_matchups_box, plot_matchups_hist
pd.options.mode.chained_assignment = None  # default='warn'

def matchup_game_finder(
					players_df_gamelogs:pd.DataFrame, 
					input_player1:str, 
					input_player2:str, 
					teammates:bool,
					exact_match:bool
				) -> pd.DataFrame:
	'''Concatenates all lists of DataFrames

		Args:
			players_df_gamelogs: all gamelogs
			player1: name of player1 for analysis
			player1: name of player2 for analysis
			exact_match: if True, fuzzy_matching_df disabled

		Returns:
			df_overlap: all games in which player1 played player2
	'''
	print('Requested {} | {}'.format(input_player1, input_player2))
	all_players_list = players_df_gamelogs['player_name'].unique()
	if exact_match:
		player1 = input_player1
		player2 = input_player2
	else:
		player1 = fuzzy_matching_df(input_player1, all_players_list)
		player2 = fuzzy_matching_df(input_player2, all_players_list)
	if player1 == '':
		print('{} not found.'.format(input_player1))
		return
	if player2 == '':
		print('{} not found.'.format(input_player2))
		return
	player_gamelogs = players_df_gamelogs[players_df_gamelogs['player_name'] == player1]
	player_gamelogs.loc[:,'matchup'] = 'Other'
	player2_gamelogs = players_df_gamelogs[players_df_gamelogs['player_name'] == player2]
	# Find overlap between player1 and player2 gamelogs by comparing dates
	players_overlap = pd.merge(player_gamelogs, player2_gamelogs, how='inner', on=['date'])
	df_overlap = pd.DataFrame(columns=player_gamelogs.columns)
	if len(players_overlap) > 0:
		if teammates:
			print('Finding games with {} and {} as teammates'.format(player1, player2))
			player2_side = 'tm'
		else:
			print('Finding games between {} and {}...'.format(player1, player2))
			player2_side = 'opp'
		for game_date in players_overlap['date'].tolist():
			game_player = player_gamelogs[player_gamelogs['date']==game_date]
			game_player2 = player2_gamelogs[player2_gamelogs['date']==game_date]
			if game_player['tm'].item() == game_player2[player2_side].item():
				df_overlap = pd.concat([df_overlap, game_player])
				# Drop date from original gamelogs
				player_gamelogs = player_gamelogs[player_gamelogs['date']!=game_date]
		df_overlap.loc[:,'matchup'] = player2
		plot_matchups_box(player_gamelogs, df_overlap, teammates)
	else:
		print('No games found.')
	return df_overlap