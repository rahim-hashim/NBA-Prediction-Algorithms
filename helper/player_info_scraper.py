import re
import sys
import requests
import pandas as pd
from bs4 import BeautifulSoup
from string import ascii_lowercase
from collections import defaultdict
from helper.Regions import stateDict
from helper.player_table_scraper import player_table_scraper

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
  # Meta Info
  ## Parse out birthCity and birthCountry
  try:
    birthPlace = soup.find(itemprop="birthPlace").get_text()
    birthCity, birthCountry = birthPlace.split(',')
    player_MetaHash['birthCountry'] = [birthCountry.strip()]
    player_MetaHash['birthCity'] = [birthCity.split('in')[1].strip()]
    #For US players, birthState column value
    if player_MetaHash['birthCountry'][0] in list(stateDict.keys()):
      player_MetaHash['birthState'] = [birthCountry]
      player_MetaHash['birthCountry'] = ['United States of America']
  except:
    pass
  meta = soup.find(id='meta')
  try:
    player_MetaHash['shootingHand'] = [re.findall('<strong>\n  Shoots:\n  </strong>\n  (.*?)\n</p>', str(meta))[0]]
  except:
    pass
  for index, i in enumerate(soup.select("strong")):
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