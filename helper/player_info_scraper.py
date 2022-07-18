import re
import sys
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from string import ascii_lowercase
from collections import defaultdict
from Regions import stateDict
from player_table_scraper import player_table_scraper

def player_info_scraper(playerName, playerURL):
	'''Scrapes data from each player's specific URL page

	Args:
		playerName: player's full name
		playerURL: player's specific URL

	Returns:
		df_row: df containing meta info on player
		df_players: df containing statistical data on player

	'''
	response = requests.get(playerURL)
	soup = BeautifulSoup(response.text, 'html.parser')
	player_MetaHash = defaultdict(list)
	
	# Birth Info
	try:
		birth_script = soup.find('script', type='application/ld+json')
		json_text = birth_script.text
		birth_data = json.loads(json_text)
		birthPlace = birth_data['birthPlace'].split(',')
		birthInfo = [info.strip() for info in birthPlace]
		# Country with states (e.g., US, Canada)
		if len(birthInfo) == 2:
			player_MetaHash['birthCity'] = birthInfo[0]
			player_MetaHash['birthState'] = 'N/A'
			player_MetaHash['birthCountry'] = birthInfo[1]
		# Country without states (e.g., Nigeria, Greece)
		if len(birthInfo) == 3:
			player_MetaHash['birthCity'] = birthInfo[0]
			player_MetaHash['birthState'] = birthInfo[1]
			player_MetaHash['birthCountry'] = birthInfo[2]
	# No player birth data
	except:
		player_MetaHash['birthCity'] = 'N/A'
		player_MetaHash['birthState'] = 'N/A'
		player_MetaHash['birthCountry'] = 'N/A'
	
	# Meta Info
	meta = soup.find(id='meta')
	## Shooting hand data
	try:
		player_MetaHash['shootingHand'] = [re.findall('<strong>\n  Shoots:\n  </strong>\n  (.*?)\n</p>', str(meta))[0]]
	except:
		pass
	## Other data
	for index, i in enumerate(soup.select("strong")):
		### High school data
		if i.get_text(strip=True) == 'High School:':
			high_school_string = i.next_sibling
			high_school_info = i.next_sibling.next_sibling
			player_MetaHash['highSchool'] = [high_school_string.split(' in ')[0].strip()]
			# US Players
			try:
				player_MetaHash['highSchoolCity'] = [high_school_string.split(' in ')[1].strip()[:-1]]
				player_MetaHash['highSchoolState'] = [re.findall('>(.*?)</a>', str(high_school_info))[0]]
				player_MetaHash['highSchoolCountry'] = ['United States of America']
			# International Players
			except:
				player_MetaHash['highSchoolCity'] = [high_school_string.split(' in ')[1].split(',')[0]]
				player_MetaHash['highSchoolState'] = ['N/A']
				player_MetaHash['highSchoolCountry'] = [high_school_string.split()[-1]]
		### Draft data
		if i.get_text(strip=True) == 'Draft:':
			draftTeam_string = i.next_sibling.next_sibling
			draftInfo_string = i.next_sibling.next_sibling.next_sibling
			try:
				player_MetaHash['draftTeam'] = [re.findall('>(.*?)</a>', str(draftTeam_string))[0]]
			except:
				pass
			draftInfo_uncleaned = re.findall('\d+', draftInfo_string)
			try:
				player_MetaHash['draftRound'] = [int(draftInfo_uncleaned[0])]
				player_MetaHash['draftRoundPick'] = [int(draftInfo_uncleaned[1])]
				player_MetaHash['draftOverallPick'] = [int(draftInfo_uncleaned[2])]
			except:
				pass
	df_row = pd.DataFrame.from_dict(player_MetaHash)
	# Statistical Data    
	df_player, df_gamelogs = player_table_scraper(playerName, soup)
	return df_row, df_player, df_gamelogs