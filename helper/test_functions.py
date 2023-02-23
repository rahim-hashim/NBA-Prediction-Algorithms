import re
import os
import sys
import numpy as np
import pandas as pd
from pprint import pprint
import matplotlib as mpl
from string import ascii_lowercase
from collections import defaultdict

# Custom functions
from player_scraper import scrape_all_players, pickle_load

def replace_win(row):
	'''Places 1 for win, 0 for loss, and NaN for DNP'''
	if row['win'][0] == 'W':
		return 1
	elif row['win'][0] == 'L':
		return 0
	else:
		return np.nan

ROOT = os.getcwd()
# Scrape players
# df_players_meta, df_players_data, df_players_gamelogs  = scrape_all_players(ROOT, THREAD_FLAG=True)

# Load player data
from player_scraper import pickle_load

DATA_PARENT = os.path.dirname(os.getcwd())
DATA_PATH = os.path.join(DATA_PARENT,'data')
sys.path.append(DATA_PATH)

players_df_meta = pickle_load(os.path.join(DATA_PATH,'players_df_meta.pkl'))
players_df_data = pickle_load(os.path.join(DATA_PATH,'players_df_data.pkl'))
players_df_gamelogs = pickle_load(os.path.join(DATA_PATH,'players_df_gamelogs.pkl'))
print('Datasets loaded.')

# DELETE THIS EVENTUALLY
# Add win (1) loss (0) field parsing from 'win' column
players_df_gamelogs['win_loss'] = players_df_gamelogs.apply(replace_win, axis=1)

# Matchup analysis
from player_matchup import matchup_game_finder
print(players_df_gamelogs.columns)

player1 = 'Steve Nash'
player2 = 'Kobe Bryant'
matchup_game_finder(players_df_gamelogs, player1, player2, 
									  teammates=False, exact_match=True)