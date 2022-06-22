import pandas as pd

def game_finder(players_df_gamelogs:pd.DataFrame, player:str, opponent:str) -> pd.DataFrame:
	'''Concatenates all lists of DataFrames

		Args:
			players_df_gamelogs: all gamelogs
			player: name of player for analysis
			player: name of opponent for analysis

		Returns:
			df_overlap: all games in which player played opponent
	'''
	player_gamelogs = players_df_gamelogs[players_df_gamelogs['player_name'] == player]
	opponent_gamelogs = players_df_gamelogs[players_df_gamelogs['player_name'] == opponent]
	players_overlap = pd.merge(player_gamelogs, opponent_gamelogs, how='inner', on=['date'])
	df_overlap = pd.DataFrame(columns=player_gamelogs.columns)
	if len(players_overlap) > 0:
		for game_date in players_overlap['date'].tolist():
			game_player = player_gamelogs[player_gamelogs['date']==game_date]
			game_opponent = opponent_gamelogs[opponent_gamelogs['date']==game_date]
			if game_player['tm'].item() == game_opponent['opp'].item():
				df_overlap = pd.concat([df_overlap, game_player])
	print('{} games found'.format(len(df_overlap)))
	return df_overlap