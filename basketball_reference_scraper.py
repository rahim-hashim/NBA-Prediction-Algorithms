import os
import sys
from helper.player_scraper import scrape_all_players, concatenate_dfs

def main(ROOT):
	list_players_meta, list_players_data, list_players_gamelogs = scrape_all_players(ROOT, THREAD_FLAG=True)
	df_players_meta, df_players_data, df_players_gamelogs = concatenate_dfs(ROOT, list_players_meta, list_players_data, list_players_gamelogs)
	return df_players_meta, df_players_data, df_players_gamelogs