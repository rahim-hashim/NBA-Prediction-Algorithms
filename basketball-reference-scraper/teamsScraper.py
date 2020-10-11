import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import date

def teamsScraper():
    '''
    teamsScraper scrapes all NBA, ABA, and BAA team info,
    including all the different names for each franchise,
    and the years in which they were active
    '''
    teamsHash = defaultdict(dict)
    url = 'https://www.basketball-reference.com/teams/'
    response = requests.get(url)
    
    # Insert all tables into Pandas DataFrame
    df_list = pd.read_html(response.text)
    teams_list = list(df_list[0]['Franchise'])
    years_list = list(df_list[0]['To'])
        
    # date object of today's date
    today = date.today()
    
    current_team = ''
    for t_index, team in enumerate(teams_list):
        if team != 'Franchise':
            if int(years_list[t_index][:4]) == int(today.year - 1): # active franchise (i.e. [2019]-2020)
                teamsHash[team] = [team]
                current_team = team
            else:
                teamsHash[current_team].append(team)
    return teamsHash