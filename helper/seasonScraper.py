import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from collections import defaultdict
from tableScraper import tableScraper

#from gameLogScraper import gameDataScraper

def seasonInfoScraper(url, seasonsHash):
    '''
    seasonInfoScraper scrapes the meta-data for each season
    '''
    # Initialize variables
    '''
    The API for basketball-reference sorts seasons by
    the end year of that season 
    (i.e. NBA Season 2019-2020 in
    https://www.basketball-
    reference.com/leagues/NBA_2020.html)
    '''
    
    league = url[-13:-10]
    year = url[-9:-5]
    
    # list of all current franchises and past names
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        #df_list = pd.read_html(response.text)
        perGame_allFields = ['ranker', 'team_name', 'g', 'mp', 'fg', 'fga',\
    'fg_pct', 'fg3', 'fg3a', 'fg3_pct', 'fg2', 'fg2a', 'fg2_pct', 'efg_pct','ft', 'fta', \
    'ft_pct', 'orb', 'drb', 'trb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts']
        table = tableScraper(perGame_allFields, year, soup, 'team-stats-per-game', 'table')
    elif response.status_code == 404:
    # Most likely because the ABA league did not exist outside of 1967-1976
        return('N/A')

