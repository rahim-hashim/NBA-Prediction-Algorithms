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

from stat_info import STAT_LIST, stat_dict, stat_precision, stat_range
from fuzzy_lookup import fuzzy_matching_df
from stat_printer import print_stats
pd.options.mode.chained_assignment = None  # default='warn'

color1 = (0.2789215686274509, 0.48774509803921573, 0.6583333333333334, 1) # blue
color2 = (0.7950980392156863, 0.2009803921568627, 0.20686274509803904, 1) # red

def plot_matchups_box(player_gamelogs, df_overlap, teammates, legend=False):
	'''
	Plots all specified stats for player1 vs. rest of nba and player2
	'''
	df_all = pd.concat([player_gamelogs, df_overlap])
	f, axarr = plt.subplots(1,len(STAT_LIST),figsize=(18,8))
	plt.style.use('fivethirtyeight')
	mpl.rcParams.update(mpl.rcParamsDefault)
	player_name = player_gamelogs['player_name'].unique()[0]
	player2_name = df_all['matchup'].unique()[1]
	for i, stat in enumerate(STAT_LIST):
		if stat == 'win_loss':
			stat_all_avg = np.nanmean(df_all[df_all['matchup'] == 'Other'][stat].tolist())
			stat_opp_avg = np.nanmean(df_all[df_all['matchup'] == player2_name][stat].tolist())
			axarr[i].scatter([0,0], [stat_all_avg,stat_opp_avg], c=[color1, color2], 
									s=350, edgecolor='black', linewidth=3)
		else:
			# stat_all_avg = np.nanmedian(df_all[df_all['matchup'] == 'Other'][stat].tolist())
			# stat_opp_avg = np.nanmedian(df_all[df_all['matchup'] == player2_name][stat].tolist())
			ax = sns.boxplot(ax=axarr[i], x='matchup', y=stat, data=df_all, 
												order=['Other', player2_name ], palette=[color1, color2],
												width=0.5, showfliers = False, whis=0, linewidth=4)
		axarr[i].set_title(stat_dict[stat], fontsize=16)
		axarr[i].set_ylim(stat_range[stat][0], stat_range[stat][1])
		# color_selected = color2 if stat_all_avg > stat_opp_avg else color1
		# axarr[1][i].bar(x=[1], height=[(stat_opp_avg-stat_all_avg)/abs(stat_opp_avg)], 
		# 							edgecolor='black', color=color_selected, width=1, linewidth=4)
		# axarr[1][i].set_xlim(0, 2)
		# axarr[1][i].axhline(y=[0], color='black', linewidth=2, linestyle='--')
		# if stat != 'plus_minus':
		# 	axarr[1][i].set_ylim(-1, 1)
		# else:
		# 	axarr[1][i].set_ylim(-2, 2)
	
	print_stats(player_gamelogs, df_overlap, STAT_LIST, teammates)
	# All subplots title
	teammate_string = 'With' if teammates else 'Versus'
	f.suptitle('{} Performance {}'.format(player_name, teammate_string), fontsize=22, y=0.98)
	for ax in axarr.flat:
		ax.set(xlabel=None)
		ax.set(ylabel=None)
		ax.set_xticks([])
		ax.set_facecolor('#f0f0f0')
		ax.yaxis.set_label_coords(0, 1.01)
		ax.set_axisbelow(True)
		ax.yaxis.grid(color='lightgrey', linestyle='dashed')
		# sns.despine(ax=ax, top=True, right=True, 
		# 									 left=False, bottom=True)

	# Background color
	rect = Rectangle((0, 0), 1, 1, facecolor='#f0f0f0', edgecolor='none',
									transform=f.transFigure, zorder=-1)
	f.patches.append(rect)
	plt.tight_layout()

	# Legend
	if legend:
		patch1 = Patch(color=color1, label='Other')
		patch2 = Patch(color=color2, label=player2_name)
		plt.figlegend(handles=[patch1, patch2], loc='upper right', ncol=2, fontsize=12)

	# Main Title
	f.text(0.49, 0.91, s='Rest of NBA', ha='right', fontsize=15, color=color1, fontweight='bold')
	f.text(0.51, 0.91, s=player2_name, ha='left', fontsize=15, color=color2, fontweight='bold')
	f.text(0.5, 0.91, s='|', ha='center', fontsize=15, color='black', fontweight='bold')
	plt.subplots_adjust(top=0.85)
	plt.show()

	# Save Figures
	last_name_player = player_name.split(' ')[-1]
	last_name_player2 = player2_name.split(' ')[-1]
	SAVE_PATH = os.path.join(os.getcwd(), 'matchup_plots')
	teammate_string = 'with' if teammates else 'vs'
	file_name = os.path.join(SAVE_PATH, '{}_{}_{}.png'.format(last_name_player, teammate_string, last_name_player2))
	if not os.path.exists(SAVE_PATH):
		os.makedirs(SAVE_PATH)
	print('Saving figure to {}'.format(file_name))
	f.savefig(file_name)

def plot_matchups_hist(player_gamelogs, df_overlap, teammates, legend=False):
	'''
	Plots all specified stats for player1 vs. rest of nba and player2
	'''
	df_all = pd.concat([player_gamelogs, df_overlap])
	f, axarr = plt.subplots(1,len(STAT_LIST)*2-1,figsize=(24,8))
	plt.style.use('fivethirtyeight')
	mpl.rcParams.update(mpl.rcParamsDefault)
	player_name = player_gamelogs['player_name'].unique()[0]
	player2_name = df_all['matchup'].unique()[1]
	stat_all = df_all[df_all['matchup'] == 'Other']
	stat_opp = df_all[df_all['matchup'] == player2_name]
	for i, stat in enumerate(STAT_LIST):
		stat_all_mean = np.mean(stat_all[stat].tolist())
		stat_opp_mean = np.mean(stat_opp[stat].tolist())
		if stat == 'win_loss':
			axarr[i].scatter([0,0], [stat_all_mean,stat_opp_mean], c=[color1, color2], 
									s=200, edgecolor='black', linewidth=3)
			axarr[i].set_title(stat_dict[stat], fontsize=16)
			axarr[i].set_ylim(stat_range[stat][0], stat_range[stat][1])
		else:
			# axarr[i*2-1].hist(stat_all[stat].tolist(), bins=20, color=color1, edgecolor='black', 
			# 							linewidth=3, alpha=0.5, orientation='horizontal', density=True)
			sns.histplot(ax=axarr[i*2-1], y=stat_all[stat].tolist(), color=color1, kde=True, stat='density')
			sns.histplot(ax=axarr[i*2], y=stat_opp[stat].tolist(), color=color2, kde=True, stat='density')
			axarr[i*2-1].set_ylim(stat_range[stat][0], stat_range[stat][1])
			axarr[i*2].set_ylim(stat_range[stat][0], stat_range[stat][1])
			axarr[i*2-1].invert_xaxis()
			axarr[i*2-1].get_shared_y_axes().join(axarr[i*2-1], axarr[i*2])
			axarr[i*2-1].set_title(stat_dict[stat], fontsize=16)
			axarr[i*2-1].yaxis.tick_left()
			axarr[i*2].yaxis.set_ticklabels([])
			plt.subplots_adjust(wspace=0)
		# All subplots title
	teammate_string = 'Versus'
	if teammates:
		teammate_string = 'With'
	f.suptitle('{} Performance {}'.format(player_name, teammate_string), fontsize=22, y=0.98)
	for ax_index, ax in enumerate(axarr.flat):
		ax.set(xlabel=None)
		ax.set(ylabel=None)
		ax.set_xticks([])
		ax.set_facecolor('#f0f0f0')
		ax.grid(True)
		ax.yaxis.set_label_coords(0, 1.01)
		# sns.despine(ax=ax, top=True, right=True, 
		# 									 left=False, bottom=True)

	# Background color
	rect = Rectangle((0, 0), 1, 1, facecolor='#f0f0f0', edgecolor='none',
									transform=f.transFigure, zorder=-1)
	f.patches.append(rect)
	f.tight_layout()

	# Subtitle
	f.text(0.49, 0.91, s=player2_name, ha='right', fontsize=15, color=color2, fontweight='bold')
	f.text(0.5, 0.91, s='|', ha='center', fontsize=15, color='black', fontweight='bold')
	f.text(0.51, 0.91, s='Rest of NBA', ha='left', fontsize=15, color=color1, fontweight='bold')
	plt.subplots_adjust(top=0.85)
	plt.show()

	# Save Figures
	last_name_player = player_name.split(' ')[-1]
	last_name_player2 = player2_name.split(' ')[-1]
	SAVE_PATH = os.path.join(os.getcwd(), 'matchup_plots')
	file_name = os.path.join(SAVE_PATH, '{}_vs_{}.png'.format(last_name_player, last_name_player2))
	if not os.path.exists(SAVE_PATH):
		os.makedirs(SAVE_PATH)
	print('Saving figure to {}'.format(file_name))
	f.savefig(file_name)