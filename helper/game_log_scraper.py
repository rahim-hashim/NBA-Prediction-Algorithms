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
from bs4 import BeautifulSoup
from collections import defaultdict

def game_log_scraper(playerName, gamelog):
  page = requests.get(gamelog)
  soup = BeautifulSoup(page.content, 'html.parser')
  season_title = soup.find('h1').text
  pattern = r'\d[0-9\-]*'
  season_re = re.findall(pattern,season_title)
  season = season_re[0]
  table = soup.find('table', {'id': 'pgl_basic'})
  # print the table headers
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
  
  header_subset = list(map(lambda x: x.lower(), header_names[1:-1])) # remove empty column and '+/-'
  header = ['player_name'] + ['season'] + header_subset + ['plus_minus']
  df = pd.DataFrame(columns=header)

  table_rows = table.find_all('tr')
  for tr in table_rows:
    dataCols = tr.find_all('td')
    data = []
    for dataVal in dataCols:
      ele = dataVal.text.strip()
      if ele.isnumeric() or ele[1:].isnumeric():
        if re.search(r'\.',ele): # float
          ele = float(ele)
        else: # int
          ele = int(ele)
      data.append(ele)
    statData = [playerName] + [season] + data
    #statData = [playerName] + season + data
    if len(statData) > 10: # fix for 'Did not Play'
      df_row = pd.DataFrame([statData], columns=header)
      df = pd.concat([df, df_row], ignore_index=True)
  return df 
