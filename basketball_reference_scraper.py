import os
import sys
from helper.player_scraper import scrape_all_players, concatenate_dfs

def main(ROOT):
	'''Runs scrape_all_players and concatenate_dfs to generate output DataFrames

	  Args:
	    ROOT: website root

	  Returns:
	    df_players_meta: meta-info on all players in database
	    df_players_data: statistics on all players in database
	    df_players_gamelogs: gamelogs of all players in database
	'''
	df_players_meta, df_players_data, df_players_gamelogs = scrape_all_players(ROOT, THREAD_FLAG=True)
	return df_players_meta, df_players_data, df_players_gamelogs