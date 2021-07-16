import re
import pandas as pd
from bs4 import BeautifulSoup, Comment
from collections import defaultdict

INCLUDED_TABLES = ['all_salaries'] # for testing
EXCLUDED_TABLES = ['highs-reg-season', 'sims-thru'] # not included in final DataFrame

def data_type_parse(tag_soup):
  id_pattern = 'id="([A-Za-z0-9_/\\-]*)'
  reg_result = re.search(id_pattern, str(tag_soup))
  reg_result = reg_result.group(1)
  data_type = reg_result.replace('_sh','').replace('div_','')
  return data_type

def row_scraper(playerName, tag_soup, tag, statHashList):
  if tag == 'caption':
    table = tag_soup.find_parent('table') # table is the parent to <caption> tag
    rows = re.findall('<tr(.*?)</tr>', str(table))
    data_category = table['id']
    data_category_split = data_category.split('_')
    data_type = '_'.join(data_category_split[1:]) # remove playoffs_
  elif tag == 'comment':
    table = tag_soup.find_all('table') # table is the child to <caption> tag
    rows = re.findall('<tr(.*?)</tr>', str(table))
    data_type = data_type_parse(tag_soup) # finds 'id=____' which is data_type
  if rows:
    if data_type in EXCLUDED_TABLES:
      return statHashList # exclude tables
    for index, row in enumerate(rows):
      statHash = defaultdict(dict)
      if index == 0: # table header
        statFields = ['player_name'] + re.findall('data-stat="(.*?)"', str(row))
      else: # table data
        row_soup = BeautifulSoup(row, 'html.parser')
        season_playoffs = ['playoffs' if 'playoff' in row_soup else 'season']
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
        statHashList.append(df_row)
  else:
    pass
  return statHashList

def player_table_scraper(playerName, playerSoup):
  '''
  tableGeneralScraper will be used to scrape all table types to insert into
  statHash. Given the generalizable nature of the html structure on each player's
  page, the location of the data is the same, with the only key differences being 
  the tables tag (statTag) and column names for each (statType).
  '''
  #with open('soup.txt', mode='wt') as file:
  #  file.write(str(playerSoup))
  statHashList = []

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