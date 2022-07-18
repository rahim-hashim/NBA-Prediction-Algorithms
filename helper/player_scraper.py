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
from collections import defaultdict

# Custom Functions
from fuzzy_lookup import fuzzy_matching_html
from meta_info_scraper import meta_info_scraper
from player_info_scraper import player_info_scraper

WEBSITE_URL = 'https://www.basketball-reference.com'
PLAYERS_ROOT_URL: str = WEBSITE_URL + '/players/'
PLAYER_META_PICKLE: str = 'players_df_meta.pkl'
PLAYER_DATA_PICKLE: str = 'players_df_data.pkl'
PLAYER_GAMELOG_PICKLE: str = 'players_df_gamelogs.pkl'


def pickle_dump(pickle_object, pickle_name):
  with open(pickle_name, 'wb') as f:
    pickle.dump(pickle_object, f)


def pickle_load(pickle_name):
  with open(pickle_name, 'rb') as f:
    pickle_object = pickle.load(f)
    return pickle_object


def sizeof_fmt(num):
  '''Calculates size of pickled files'''
  for unit in [' ', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']:
    if abs(num) < 1024.0:
      return '%3.1f%s' % (num, unit)
    num /= 1024.0
  return '%.1f%s' % (num, 'Yi')



def concatenate_dfs(ROOT, list_players_meta, list_players_data, list_players_gamelogs):
  '''Concatenates all lists of DataFrames

    Args:
      ROOT: website root
      list_players_meta: list of player metadata DataFrames
      list_players_data: list of player season statistics DataFrames
      list_players_gamelogs: list of player gamelogs DataFrames

    Returns:
      df_players_meta: meta-info on all players in database
      df_players_data: statistics on all players in database
      df_players_gamelogs: gamelogs of all players in database
  '''

  SAVE_PATH = ROOT + '/data/'
  # Search for data folder
  if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

  # Concatenate all meta info and player data into three DataFrames
  print('  Concatenating DataFrames')
  start_time = time.time()
  df_players_meta = pd.concat(list_players_meta)
  df_players_data = pd.concat(list_players_data)
  df_players_gamelogs = pd.concat(list_players_gamelogs)
  end_time = time.time()
  print('  Concatenating complete')
  print('  Run Time: {} min'.format(str((end_time - start_time) / 60)[:6]))

  # Player Metadata
  print('Saving {}'.format(PLAYER_META_PICKLE))
  print('  Path: {}'.format(SAVE_PATH + PLAYER_META_PICKLE))
  df_players_meta.replace('NaN', np.nan, inplace=True)
  df_players_meta.replace('', np.nan, inplace=True)
  pickle_dump(df_players_meta, SAVE_PATH + PLAYER_META_PICKLE)
  print('  Size (meta info): {}'.format(sizeof_fmt(sys.getsizeof(df_players_meta))))

  # Player Statistics
  print('Saving {}'.format(PLAYER_DATA_PICKLE))
  print('  Path: {}'.format(SAVE_PATH + PLAYER_DATA_PICKLE))
  df_players_data.replace('NaN', np.nan, inplace=True)
  df_players_data.replace('', np.nan, inplace=True)
  pickle_dump(df_players_data, SAVE_PATH + PLAYER_DATA_PICKLE)
  print('  Size (player data): {}'.format(sizeof_fmt(sys.getsizeof(df_players_data))))

  # Gamelogs
  print('Saving {}'.format(PLAYER_GAMELOG_PICKLE))
  print('  Path: {}'.format(SAVE_PATH + PLAYER_GAMELOG_PICKLE))
  df_players_gamelogs.replace('NaN', np.nan, inplace=True)
  df_players_gamelogs.replace('', np.nan, inplace=True)
  pickle_dump(df_players_gamelogs, SAVE_PATH + PLAYER_GAMELOG_PICKLE)
  print('  Size (player data): {}'.format(sizeof_fmt(sys.getsizeof(df_players_gamelogs))))

  print('Complete.')

  # Return Players DataFrame
  return df_players_meta, df_players_data, df_players_gamelogs


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
      df_players_gamelogs: gamelogs of all players in database
  '''

  SAVE_PATH = os.path.join(ROOT, 'data')
  # Search for data folder
  if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

  # Read pickle(s)
  all_pickles = [False, False, False]
  if PLAYER_META_PICKLE in os.listdir(SAVE_PATH):
    print('{} already exists'.format(PLAYER_META_PICKLE))
    print('  Uploading...')
    df_players_meta = pd.read_pickle(SAVE_PATH + PLAYER_META_PICKLE)
    all_pickles[0] = True
  if PLAYER_DATA_PICKLE in os.listdir(SAVE_PATH):
    print('{} already exists'.format(PLAYER_DATA_PICKLE))
    print('  Uploading...')
    df_players_data = pd.read_pickle(SAVE_PATH + PLAYER_DATA_PICKLE)
    all_pickles[1] = True
  if PLAYER_GAMELOG_PICKLE in os.listdir(SAVE_PATH):
    print('{} already exists'.format(PLAYER_GAMELOG_PICKLE))
    print('  Uploading...')
    df_players_gamelogs = pd.read_pickle(SAVE_PATH + PLAYER_GAMELOG_PICKLE)
    all_pickles[2] = True

  if all(all_pickles):
    pass
  # Scrape all basketball-reference player data and pickle
  else:
    list_players_meta = []
    list_players_data = []
    list_players_gamelogs = []
    urls_players = []
    limit = 0
    for letter in ascii_lowercase:
      url = PLAYERS_ROOT_URL + letter
      urls_players.append(url)

    start_datetime = datetime.datetime.now()
    start_time = time.time()
    print('Running meta_info_scraper.py')
    print('  Start Time:', str(start_datetime.time())[:11])

    # Sequential-Processing
    if THREAD_FLAG == False:
      print('  Threading inactivated...')
      for url in urls_players:
        list_players_meta, list_players_data, list_players_gamelogs = meta_info_scraper(url, list_players_meta,
                                                                                        list_players_data,
                                                                                        list_players_gamelogs)
    # Parallel-Processing
    else:
      print('  Threading activated...')
      threads = []
      for url in urls_players:
        thread = threading.Thread(target=meta_info_scraper,
                                  args=(url, list_players_meta, list_players_data, list_players_gamelogs,))
        threads += [thread]
        thread.start()
      for thread in threads:
        thread.join()  # makes sure that the main program waits until all threads have terminated
    end_time = time.time()
    print('  Scraping complete')
    print('  Run Time: {} min'.format(str((end_time - start_time) / 60)[:6]))

    # Concatenate dfs
    df_players_meta, df_players_data, df_players_gamelogs = concatenate_dfs(ROOT, list_players_meta, list_players_data, list_players_gamelogs)

  return df_players_meta, df_players_data, df_players_gamelogs


def single_player_scraper(player_name=None):
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
      df_players_gamelogs: gamelogs of single player (if exists)
  '''
  if player_name == None:
    player_name = input('Player Name: ')
  try:
    last_name_letter = player_name.split()[1][0]  # first and last name
  except:
    last_name_letter = player_name[0][0]  # only one name
  letter_url = PLAYERS_ROOT_URL + last_name_letter.lower()
  print('Searching for name in: {}'.format(letter_url))  # organized by last name letter
  letter_response = requests.get(letter_url)
  letter_soup = BeautifulSoup(letter_response.text, 'html.parser')
  playerTableAll = letter_soup.find_all('tr')
  playerTable = iter(playerTableAll)
  next(playerTable)

  # fuzzy lookup for best name-matching
  playerName, playerURL = fuzzy_matching_html(player_name, playerTable)
  if playerName:
    df_player_meta, df_player_data, df_player_gamelogs = player_info_scraper(playerName, playerURL)
    return df_player_meta, df_player_data, df_player_gamelogs
  else:
    print('{} not found'.format(player_name))
    return None, None, None  # name missing from basketball-reference database
