
from stat_info import STAT_LIST, stat_dict, stat_precision, stat_range

def print_stats(player_gamelogs, df_overlap, STAT_LIST, teammates):
	teammate_string = 'with' if teammates else 'vs'
	for stat in STAT_LIST:
		print('  other: {} | {}: {} {}'.format(round(player_gamelogs[stat].mean(),stat_precision[stat]),
																					 teammate_string,
														 							 round(df_overlap[stat].mean(), stat_precision[stat]),
														 							 stat_dict[stat]))