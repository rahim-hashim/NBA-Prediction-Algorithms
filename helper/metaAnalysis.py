import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint
from collections import defaultdict, Counter, OrderedDict

from Regions import stateDict #stateDict is a Dictionary to help with geography-based analyses

def metaPlot(players_df_meta):
	
	height_list = players_df_meta['height'].tolist()
	weight_list = players_df_meta['weight'].tolist()
	#rightCount = 0; leftCount = 0; noHandCount = 0

	#Plot Height Distribution (1, Left)
	f, ax = plt.subplots(1,2)
	#Sets default plot size
	plt.rcParams['figure.figsize'] = (10,8)
	n1, bins1, patches1 = ax[0].hist(height_list, bins=20, density=True, histtype='bar', ec='black')
	#Converting y-axis labels from decimals to percents
	y_vals = ax[0].get_yticks(); ax[0].set_yticklabels(['{:3.1f}%'.format(y*100) for y in y_vals])
	#Converting x-axis labels from inches back to feet
	xticks1 = ['5-0', '5-6', '6-0', '6-6', '7-0', '7-6', '8-0']
	ax[0].set_xticks([60, 66, 72, 78, 84, 90, 96])
	ax[0].set_xticklabels(xticks1)
	ax[0].set_xlim([56,100])
	ax[0].set_xlabel('Height', fontweight='bold', labelpad=10)
	ax[0].set_ylabel('Percent of Players', fontweight='bold', labelpad=10)

	#Plot Weight Distribution (1, Middle)
	ax[1].hist(weight_list, bins='auto', density=True, histtype='bar', ec='black')
	y_vals = ax[1].get_yticks()
	ax[1].set_yticklabels(['{:3.1f}%'.format(y*100) for y in y_vals])
	xticks2 = ['150', '180', '210', '240', '270', '300', '330']
	ax[1].set_xticks([150, 180, 210, 240, 270, 300, 330])
	ax[1].set_xticklabels(xticks2)
	ax[1].set_xlim([120,360])
	ax[1].set_xlabel('Weight', fontweight='bold', labelpad=10)
	ax[1].set_ylabel('Percent of Players', fontweight='bold', labelpad=10)
	
	plt.tight_layout(pad=0.05, w_pad=1, h_pad=1.0)
	f.set_size_inches(18.5, 10.5, forward=True)
	plt.show()

def geographyPlot(players_df_meta):
  countryList = players_df_meta['birthCountry'].tolist()
  #countryList contains all players born in ex-US
  countryList = filter(lambda x: x != 'United States of America', countryList)
  countryList = filter(lambda x: x != '', countryList)
  countryHash = dict(Counter(countryList))
  countryHash = OrderedDict(sorted(countryHash.items(), reverse=True, key=lambda t: t[1]))

  pprint(countryHash.keys())

  #Plot Birth Countries of non-US-Born Players (3)
  max_countries = 30
  f, ax = plt.subplots(1)
  countryList = list(countryHash.keys())[:max_countries]
  countryVals = list(countryHash.values())[:max_countries]
  ax.bar(np.arange(len(countryList)), countryVals, ec='black')
  ax.set_xticks(np.arange(len(countryList)))
  ax.set_xticklabels(countryList, rotation=45, ha='right', fontsize=10)
  ax.set_xlabel('Country of Birth', fontweight='bold', labelpad=10)
  ax.set_ylabel('Number of Players', fontweight='bold', labelpad=10)
  
  f.set_size_inches(18.5, 10.5, forward=True)
  plt.show()