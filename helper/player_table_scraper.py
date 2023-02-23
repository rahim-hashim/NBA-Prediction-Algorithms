import re
import numpy as np
import pandas as pd
from IPython.display import display
from collections import defaultdict
from bs4 import BeautifulSoup, Comment
from helper.game_log_scraper import game_log_scraper
from helper.lineup_scraper import lineup_scraper
from helper.parse_tools import num_convert, data_type_parse


INCLUDED_TABLES = ['pbp'] # for testing
EXCLUDED_TABLES = ['highs-reg-season', 'sims-thru', 'adjooting'] # not included in final DataFrame
DOUBLE_HEADER_TABLES = ['pbp', 'shooting'] # tables that have two headers

WEBSITE_URL = 'https://www.basketball-reference.com'

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
  
  # If the table has rows
  if rows:
    if data_type in EXCLUDED_TABLES or data_type == '':# or data_type not in INCLUDED_TABLES:
      return statHashList # exclude tables
    # Iterates through all rows of table
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
          ele = num_convert(ele)
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
  # The table has no rows (empty)
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
  # Print soup (for debugging)
  # with open('soup.txt', mode='wt') as file:
  #  file.write(str(playerSoup))
  statHashList = []

  # Season Data (Per Game, Totals, Advanced Tables)
  for caption_soup in playerSoup.find_all('caption'):
    statHashList = row_scraper(playerName, caption_soup, 'caption', statHashList)

  # Season Data (Per 36 Minutes, Per 100 Poss, Adjusted Shooting, Play-by-Play, Shooting)
  # Tables all hidden in html comments (<!---->)
  for comment in playerSoup.find_all(text=lambda text: isinstance(text, Comment)):
    if comment.find('<caption>') > 0:
      comment_soup = BeautifulSoup(comment, 'html.parser')
      statHashList = row_scraper(playerName, comment_soup, 'comment', statHashList)


  links = playerSoup.find_all('a', href=True) # pull all links from player page

  # Gamelogs Scraper
  gamelogs = np.unique(np.array([link['href'] for link in links if 'gamelog' in str(link)]))
  gamelogs_df = pd.DataFrame()
  for gamelog in gamelogs:
    gamelog_url = WEBSITE_URL + gamelog
    #gamelog_advanced_url = gamelog_url.replace('gamelog', 'gamelog-advanced')
    if 'playoffs' not in gamelog_url: # playoff gamelogs will be captured by individual season gamelog scraper
      try:
        gamelog_df = game_log_scraper(playerName, gamelog_url)
        gamelogs_df = pd.concat([gamelogs_df,gamelog_df])
      except:
        pass # unique situations where gamelogs are listed on player page but the table doesn't exist

  # Lineups Scraper
  lineups = np.unique(np.array([link['href'] for link in links if 'lineups' in str(link)]))
  lineups_df = pd.DataFrame()
  for lineup in lineups:
    lineup_url = WEBSITE_URL + lineup
    if 'playoffs' not in lineup_url:
      try:
        lineup_df = lineup_scraper(playerName, lineup_url)
        lineups_df = pd.concat([lineups_df,lineup_df])
      except:
        pass

  df_player = pd.concat(statHashList, ignore_index=True)
  return df_player, gamelogs_df