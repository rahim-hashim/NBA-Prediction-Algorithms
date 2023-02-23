STAT_LIST = ['win_loss', 'pts', 'fg%', 'trb', 'ast', '3p%', 'tov', 'gmsc', 'plus_minus']

stat_dict = {
	'win_loss': 'Win/Loss %',
	'pts': 'Points',
	'fg%': 'Field Goal %',
	'trb': 'Total Rebounds',
	'ast': 'Assists',
	'tov': 'Turnovers',
	'3p%': '3pt %',
	'gmsc': 'Game Score',
	'plus_minus': 'Plus/Minus'
}

stat_precision = {
	'win_loss': 2,
	'pts': 1,
	'fg%': 3,
	'trb': 1,
	'ast': 1,
	'tov': 1,
	'3p%': 3,
	'gmsc': 2,
	'plus_minus': 2
}

stat_range = {
	'win_loss': [0, 1],
	'pts': [0, 50],
	'fg%': [0, 1],
	'trb': [0, 20],
	'ast': [0, 10],
	'tov': [0, 10],
	'3p%': [0, 1],
	'gmsc': [0, 30],
	'plus_minus': [-25, 25]
}