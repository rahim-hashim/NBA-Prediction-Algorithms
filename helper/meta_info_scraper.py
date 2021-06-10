import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from collections import defaultdict
from PlayerObject import Player
from player_info_scraper import player_info_scraper

def meta_info_scraper(url, list_players_meta, list_players_data):
  meta_hash = defaultdict(list)
  '''
  metaInfoScraper scrapes the meta-data on each player
  '''
  allPlayerCounter = 0; playerDataCounter = 0
  letterPlayerCounter = 0
  '''
  The API for basketball-reference sorts players by last name first letter 
  (i.e. Kobe Bryant in https://www.basketball-reference.com/players/b/)
  '''
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html.parser')
  '''
  In order to find exactly where all the data is housed, I view the website on 
  Google Chrome and use the developer tools pointer. Here, we can see
  that the tag for the table holding all important data is 'tr'
  For additional help on HTML/tags: https://www.dataquest.io/blog/web-scraping-tutorial-python/
  '''
  playerTableAll = soup.find_all('tr')
  #Header to playerTable is descriptive and not a player -> skip line
  playerTable = iter(playerTableAll); next(playerTable)
  for index, row in enumerate(playerTable):
    '''
    Once the table is pulled in as playerTable, we'll be using re.findall
    to parse out the text in each field listed below, taking the first element [0]
    given that the results will always be a list with one element, and we 
    want a string to insert as an attribute in the player class
    '''
    player_name = re.findall('.html">(.*?)</a>', str(row))[0]
    meta_hash['player_name'] = [player_name]
    meta_hash['draft_year'] = [re.findall('data-stat="year_min">(.*?)</td>', str(row))[0]]
    meta_hash['retire_year'] = [re.findall('data-stat="year_max">(.*?)</td>', str(row))[0]]
    height = re.findall('data-stat="height">(.*?)</td>', str(row))[0]
    #Converting height from string 'FEET-INCHES' to int INCHES
    try:
      height_split = height.split('-')
      meta_hash['height'] = [int(height_split[0])*12 + int(height_split[1])]
    except:
      pass
    #Converting weight from string to int
    weight = re.findall('data-stat="weight">(.*?)</td>', str(row))[0]
    try:
      meta_hash['weight'] = [int(weight)]
    except:
      pass
    birthDate = re.findall('data-stat="birth_date">(.*?)</td>', str(row))
    #Some players do not have birthdates listed
    try:
      meta_hash['birth_date'] = [re.findall('>(.*?)</a>', str(birthDate))[0]]
    except:
      pass
    colleges = [re.findall('data-stat="colleges">(.*?)</td>', str(row))]
    #Same with colleges not being listed for some of the early players
    try:
        meta_hash['college'] = [re.findall('>(.*?)</a>', str(colleges))[0]]
    except:
        pass
    #playerURL will lead us to each player's own page, which contains the trove
    #of statistics that we will use in future analyses
    playerURL = re.findall('a href="(.*?)">', str(row))
    playerURL = 'https://www.basketball-reference.com' + playerURL[0]
    #playerOverview = playerName, draftYear, retireYear, height, weight, birthDate, colleges, playerURL
    
    '''Running playerDataScraper to capture playerData'''
    player_meta_info, df_player = player_info_scraper(player_name, playerURL)
    
    '''Creating Player object and inserting to playerHash'''
    #allPlayerInfo = playerOverview + player_meta_info
    df_player_meta = pd.DataFrame.from_dict(meta_hash)
    list_players_meta.append(df_player_meta)
    list_players_data.append(df_player)
    letterPlayerCounter += 1; allPlayerCounter += 1
  print ('\t  ' + url[-1] + '\' Players Captured: ', letterPlayerCounter)
  return list_players_meta, list_players_data

    