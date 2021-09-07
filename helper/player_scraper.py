import re
import os
import sys
import time
import requests
import datetime
import threading
import numpy as np
import pandas as pd
from tqdm import tqdm
import pickle as pickle
from timeit import timeit
from bs4 import BeautifulSoup
from string import ascii_lowercase
from helper.meta_info_scraper import meta_info_scraper
from helper.player_info_scraper import player_info_scraper

WEBSITE_URL = 'https://www.basketball-reference.com/'
PLAYERS_ROOT_URL = WEBSITE_URL + 'players/'
PLAYER_META_PICKLE = 'players_df_meta.pkl'
PLAYER_DATA_PICKLE = 'players_df_data.pkl'

def sizeof_fmt(num):
  '''Calculates size of pickled files'''
  for unit in [' ','KB','MB','GB','TB','PB','EB','ZB']:
    if abs(num) < 1024.0:
      return '%3.1f%s' % (num, unit)
    num /= 1024.0
  return '%.1f%s' % (num, 'Yi')

# Thread flag decides whether you want to use parallel processing or standard
def scrape_all_players(ROOT, THREAD_FLAG=True):
  '''Scrapes all basketball-reference player data, which includes:
    - meta information
      i.e. https://www.basketball-reference.com/players/
    - season and playoff information
      i.e. https://www.basketball-reference.com/players/b/bryanko01.html

    Args:
      ROOT: website root
      THREAD_FLAG: boolean for threading

    Returns:
      df_players_meta: meta-info on all players in database
      df_players_data: statistics on all players in database
  '''

  SAVE_PATH = ROOT + 'data/'
  # Search for data folder
  if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

  # Read pickle
  if PLAYER_META_PICKLE in os.listdir(SAVE_PATH) and PLAYER_DATA_PICKLE in os.listdir(SAVE_PATH): 
    print('{} and {} already exists'.format(PLAYER_META_PICKLE, PLAYER_DATA_PICKLE))
    print('  Uploading...')
    df_players_meta = pd.read_pickle(SAVE_PATH+PLAYER_META_PICKLE)
    df_players_data = pd.read_pickle(SAVE_PATH+PLAYER_DATA_PICKLE)
  
  # Scrape all basketball-reference player data and pickle
  else:
    list_players_meta = []
    list_players_data = []
    urls_players = []
    for letter in ascii_lowercase:
        url = PLAYERS_ROOT_URL + letter
        urls_players.append(url)

    start_datetime = datetime.datetime.now()
    start_time = time.time()
    print ('Running meta_info_scraper.py')
    print ('  Start Time:', str(start_datetime.time())[:11])

    # Sequential-Processing
    if THREAD_FLAG == False:
      print('  Threading inactivated...')
      for url in urls_players:
        list_players_meta, list_players_data = meta_info_scraper(url, list_players_meta, list_players_data)

    # Parallel-Processing
    else:
      print('  Threading activated...')
      threads = []
      for url in urls_players:
        thread = threading.Thread(target=meta_info_scraper, args=(url,list_players_meta,list_players_data,))
        threads += [thread]
        thread.start()
      for thread in threads:
        thread.join() # makes sure that the main program waits until all threads have terminated
    end_time = time.time()
    print ('  Scraping complete')
    print ('  Run Time: {} min'.format(str((end_time - start_time)/60)[:6]))
    
    # Concatenate all meta info and player data into two DataFrames
    print ('  Concatenating DataFrames')
    start_time = time.time()
    df_players_meta = None
    df_players_data = None
    for (df_meta, df_data) in tqdm(list(zip(list_players_meta, list_players_data))):
      df_players_meta = pd.concat(df_meta)
      df_players_data = pd.concat(df_data)
    end_time = time.time()
    print ('  Concatenating complete')
    print ('  Run Time: {} min'.format(str((end_time - start_time)/60)[:6]))


    print('Saving {}'.format(PLAYER_META_PICKLE))
    print('  Path: {}'.format(SAVE_PATH+PLAYER_META_PICKLE))
    df_players_meta.replace('NaN', np.nan, inplace=True)
    df_players_meta.replace('', np.nan, inplace=True)
    df_players_meta.to_pickle(SAVE_PATH+PLAYER_META_PICKLE)
    print('Saving {}'.format(PLAYER_DATA_PICKLE))
    print('  Path: {}'.format(SAVE_PATH+PLAYER_DATA_PICKLE))
    df_players_data.replace('NaN', np.nan, inplace=True)
    df_players_data.replace('', np.nan, inplace=True)
    df_players_data.to_pickle(SAVE_PATH+PLAYER_DATA_PICKLE)

  print('  Size (meta info): {}'.format(sizeof_fmt(sys.getsizeof(df_players_meta))))
  print('  Size (player data): {}'.format(sizeof_fmt(sys.getsizeof(df_players_data))))
  print('Complete.')

  # Return Players DataFrame   
  return df_players_meta, df_players_data

def single_player_scraper(player_name = None):
  '''
  single_player_scraper scrapes a single, raw inputted player
    - meta information
      i.e. https://www.basketball-reference.com/players/
    - season and playoff information
      i.e. https://www.basketball-reference.com/players/b/bryanko01.html

    Args:
      player_name: raw input of player for search

    Returns:
      df_players_meta: meta-info on single player (if exists)
      df_players_data: statistics on single player (if exists)
  '''
  if player_name == None:
    player_name = input('Player Name: ')
  try:
    last_name_letter = player_name.split()[1][0] # first and last name
  except:
    last_name_letter = player_name[0][0] # only one name
  letter_url = PLAYERS_ROOT_URL + last_name_letter.lower()
  print('Searching for name in: {}'.format(letter_url)) # organized by last name letter
  letter_response = requests.get(letter_url)
  letter_soup = BeautifulSoup(letter_response.text, 'html.parser')
  playerTableAll = letter_soup.find_all('tr')
  playerTable = iter(playerTableAll); next(playerTable)
  for index, row in enumerate(playerTable):
    row_player_name = re.findall('.html">(.*?)</a>', str(row))[0]
    if player_name.lower() == row_player_name.lower():
      playerURL = re.findall('a href="(.*?)">', str(row))
      playerURL = WEBSITE_URL + playerURL[0]
      player_meta_info, df_player = player_info_scraper(player_name, playerURL)
      print('{} found. DataFrames generated'.format(player_name))
      return player_meta_info, df_player
    else:
      continue
  print('{} not found'.format(player_name))
  return None, None # name missing from basketball-reference database