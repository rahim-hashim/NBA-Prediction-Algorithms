import re
import os
import sys
import time
import pandas as pd
from bs4 import BeautifulSoup
from string import ascii_lowercase
from collections import defaultdict

def player_table_scraper(playerName, playerSoup):
  '''
  tableGeneralScraper will be used to scrape all table types to insert into
  statHash. Given the generalizable nature of the html structure on each player's
  page, the location of the data is the same, with the only key differences being 
  the tables tag (statTag) and column names for each (statType).
  '''
  statHashList = []
  for caption in playerSoup.find_all('caption'):
    table = caption.find_parent('table')
    rows = re.findall('<tr(.*?)</tr>', str(table))
    if rows:
      for index, row in enumerate(rows):
        statHash = defaultdict(dict)
        if index == 0:
          statFields = ['player_name'] + re.findall('data-stat="(.*?)"', str(row))
        else:
          row1 = BeautifulSoup(row, 'html.parser')
          seasonCol = row1.find('th')
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
          dataCols = row1.find_all('td')
          data = [ele.text.strip() for ele in dataCols]
          if len(data) < 5:
            continue # row has mostly empty data
          statData = [playerName] + season + data
          for f_index, field in enumerate(statFields):
            statHash[field] = [statData[f_index]]
          df_row = pd.DataFrame.from_dict(statHash)
          data_category = table['id']
          if 'playoffs' in data_category:
            data_category_split = data_category.split('_')
            data_type = '_'.join(data_category_split[1:]) # remove playoffs_
            season_playoffs = 'playoffs'
          else:
            data_type = data_category
            season_playoffs = 'season'
          df_row.insert(0, 'data_type', data_type)
          df_row.insert(1, 'season_playoffs', season_playoffs)
          statHashList.append(df_row)
    else:
      continue
  df_player = pd.concat(statHashList, ignore_index=True)
  return df_player
