import re
import os
import sys
import time
import requests
import datetime
import numpy as np
import pandas as pd
from tqdm import tqdm
import pickle as pickle
from timeit import timeit
from bs4 import BeautifulSoup, Comment
from collections import defaultdict
from parse_tools import data_type_parse, num_convert 

def check_dnp(header, statData):
	if len(statData) < 6: # empty row
		return statData
	elif len(statData) < 14: # Not empty but DnD for specific reason
		empty_data = [np.nan]*(len(header) - len(statData))
		note = [statData[-1]]
		statData = statData[:-1] + empty_data + note
	else:
		statData = statData + ['']
	return statData

def gamelog_season(df_season, playerName, header, season, table):
	table_rows = table.find_all('tr')
	rk = 0 # counting game number (i.e. not blank rows)
	for tr in table_rows:
		dataCols = tr.find_all('td')
		data = []
		for dataVal in dataCols:
			ele = dataVal.text.strip()
			ele = num_convert(ele)
			data.append(ele)
		statData = [playerName, season, 'season', rk] + data
		statData = check_dnp(header, statData)
		# confirming that header and data have equal numbers of fields
		if len(header) == len(statData):
			rk += 1; statData[3] = rk # iterating only full games 
			df_row = pd.DataFrame([statData], columns=header)
			df_season = pd.concat([df_season, df_row], ignore_index=True)
	return df_season

def gamelog_playoffs(df_playoffs, playerName, header, season, comment):
	comment_soup = BeautifulSoup(comment, 'html.parser')
	playoff_table = comment_soup.find_all('table') # table is the child to <caption> tag
	rk = 0 # counting game number (i.e. not blank rows)
	rows = re.findall('<tr(.*?)</tr>', str(playoff_table))
	data_type = data_type_parse(comment_soup) # finds 'id=____' which is data_type
	if rows:
		df_playoffs = pd.DataFrame(columns=header)
		for index, row in enumerate(rows):
			statHash = defaultdict(dict)
			row_soup = BeautifulSoup(row, 'html.parser')
			dataCols = row_soup.find_all('td')
			data = []
			for dataVal in dataCols:
				ele = dataVal.text.strip()
				ele = num_convert(ele)
				data.append(ele)
			statData = [playerName, season, 'playoffs', rk] + data
			statData = check_dnp(header, statData)
			# confirming that header and data have equal numbers of fields
			if len(header) == len(statData):
				rk += 1; statData[3] = rk # iterating only full games 
				df_row = pd.DataFrame([statData], columns=header)
				df_playoffs = pd.concat([df_playoffs, df_row], ignore_index=True)
		return df_playoffs
	return None

def lineup_scraper(playerName, lineup_url):
	page = requests.get(lineup_url)
	soup = BeautifulSoup(page.content, 'html.parser')
	season_title = soup.find('h1').text
	pattern = r'\d[0-9\-]*'
	season_re = re.findall(pattern,season_title)
	season = season_re[0]
	table = soup.find('table', {'id': 'pgl_basic'})

	# find table header (i.e. fields)
	table_header = table.find('thead')
	header_cols = table_header.find_all('th')
	header_names = []
	for h_index, header in enumerate(header_cols):
		if u'\xa0' in header.get_text():
			if h_index < 7: # '' -> LOC
				header_names.append('LOC')
			else: # '' -> WIN
				header_names.append('WIN')
		else:
			header_names.append(header.get_text())
	header_names[-1] = header_names[-1].replace('+/-', 'plus_minus') # replace '+/-'
	header_subset = list(map(lambda x: x.lower(), header_names)) 
	header = ['player_name', 'season', 'season_playoffs'] + header_subset + ['note'] # note in case 'DNP' for specific reason
	df_season = pd.DataFrame(columns=header)

	# season gamelogs
	df_season = gamelog_season(df_season, playerName, header, season, table)

	# playoff gamelogs
	df_playoffs = None
	for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
		if comment.find('<caption>') > 0:
			df_playoffs = gamelog_playoffs(df_playoffs, playerName, header, season, comment)
	
	# combine season gamelogs and playoff gamelogs (if exists)
	if not isinstance(df_playoffs, type(None)):
		df = pd.concat([df_season, df_playoffs], ignore_index=True)
	else:
		df = df_season

	return df 