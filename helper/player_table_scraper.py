import re
import numpy as np
import pandas as pd
from collections import defaultdict
from bs4 import BeautifulSoup, Comment
from game_log_scraper import game_log_scraper

INCLUDED_TABLES = ['pbp'] # for testing
EXCLUDED_TABLES = ['highs-reg-season', 'sims-thru', 'adjooting'] # not included in final DataFrame
DOUBLE_HEADER_TABLES = ['pbp', 'shooting'] # tables that have two headers

WEBSITE_URL = 'https://www.basketball-reference.com'

def data_type_parse(tag_soup):
  '''Searches for tag id'''
  id_pattern = 'id="([A-Za-z0-9_/\\-]*)'
  reg_result = re.search(id_pattern, str(tag_soup))
  reg_result = reg_result.group(1)
  data_type = reg_result.replace('_sh','').replace('div_','')
  return data_type

def row_scraper(playerName, tag_soup, tag, statHashList):
  if tag == 'caption':
    table = tag_soup.find_parent('table') # table is the parent to <caption> tag
    rows = re.findall('<tr(.*?)</tr>', str(table))
    data_type = table['id']
  elif tag == 'comment':
    table = tag_soup.find_all('table') # table is the child to <caption> tag
    rows = re.findall('<tr(.*?)</tr>', str(table))
    data_type = data_type_parse(tag_soup) # finds 'id=____' which is data_type
  season_playoffs = 'season'
  if 'playoffs' in data_type:
    season_playoffs = 'playoffs'
    data_type = data_type.replace('playoffs_', '') # remove playoffs_
  if rows:
    if data_type in EXCLUDED_TABLES or data_type == '':# or data_type not in INCLUDED_TABLES:
      return statHashList # exclude tables
    for index, row in enumerate(rows):
      statHash = defaultdict(dict)
      if index == 0: # table header
        statFields = ['player_name'] + re.findall('data-stat="(.*?)"', str(row))
        if data_type in DOUBLE_HEADER_TABLES:
          continue
      elif data_type in DOUBLE_HEADER_TABLES and index == 1:
        statFields = ['player_name'] + re.findall('data-stat="(.*?)"', str(row))
      else: # table data
        row_soup = BeautifulSoup(row, 'html.parser')
        if 'playoffs' in str(row_soup): # second check for playoff data
          season_playoffs = 'playoffs' 
        seasonCol = row_soup.find('th')
        if seasonCol == None:
          continue # missing data
        seasonData = seasonCol.text.strip()
        if seasonData == 'Career':
          season = ['Career']
        elif '-' in str(seasonData):
          seasonSplit = seasonData.split('-')
          if len(seasonSplit) == 2:
            season = [seasonSplit[0][-4:] + '-' + seasonSplit[1][:2]]
          else:
            # ignoring non-year / non-career listings (i.e. team-specific stats)
            continue
        else:
          continue # team-specific stats
        dataCols = row_soup.find_all('td')
        data = []
        for dataVal in dataCols:
          ele = dataVal.text.strip()
          if ele.isnumeric():
            if re.search(r'\.',ele): # float
              ele = float(ele)
            else: # int
              ele = int(ele)
          data.append(ele)
        statData = [playerName] + season + data
        for f_index, field in enumerate(statFields):
          statHash[field] = [statData[f_index]]
        df_row = pd.DataFrame.from_dict(statHash)
        df_row.insert(0, 'data_type', data_type)
        df_row.insert(1, 'season_playoffs', season_playoffs)
        if 'DUMMY' in df_row.columns:
          df_row = df_row.drop(['DUMMY'], axis=1)
        statHashList.append(df_row)
  else:
    pass
  return statHashList

def player_table_scraper(playerName, playerSoup):
  '''Scrape all table types to insert into pandas DataFrame

  Args:
    playerName: player's full name
    playerSoup: player's URL after BeautifulSoup

  Returns:
    df_players: df containing statistical data on player
  
  Given the generalizable nature of the html structure on each player's
  page, the location of the data is the same, with the only key differences being 
  the tables tag (statTag) and column names for each (statType).
  '''
  #with open('soup.txt', mode='wt') as file:
  #  file.write(str(playerSoup))
  statHashList = []

  # pull all links from player page
  links = playerSoup.find_all('a', href=True)
  gamelogs = np.unique(np.array([link['href'] for link in links if 'gamelog' in str(link)]))
  lineups = np.unique(np.array([link['href'] for link in links if 'lineups' in str(link)]))

  for gamelog in gamelogs:
    gamelog_url = WEBSITE_URL + gamelog
    if 'playoffs' in gamelog_url:
      continue
    else:
      gamelog_advanced_url = gamelog_url.replace('gamelog', 'gamelog-advanced')
    game_log_scraper(gamelog_url)
    game_log_scraper(gamelog_advanced_url)

  # Per Game, Totals, Advanced Tables
  for caption_soup in playerSoup.find_all('caption'):
    statHashList = row_scraper(playerName, caption_soup, 'caption', statHashList)

  # Per 36 Minutes, Per 100 Poss, Adjusted Shooting, Play-by-Play, Shooting
  # Tables all hidden in html comments (<!---->)
  for comment in playerSoup.find_all(text=lambda text: isinstance(text, Comment)):
    if comment.find('<caption>') > 0:
      comment_soup = BeautifulSoup(comment, 'html.parser')
      statHashList = row_scraper(playerName, comment_soup, 'comment', statHashList)

  df_player = pd.concat(statHashList, ignore_index=True)
  return df_player