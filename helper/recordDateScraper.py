# recordDateScraper.py
# Aunoy Poddar
# 09_18_2020
# Helper function to create a hash for a season keeping track of team
# records at a particular date by scraping basketball reference
# with Rahim Hashim.

import re
import requests
from bs4 import BeautifulSoup
from string import ascii_lowercase
from collections import defaultdict
from itertools import zip_longest
from TeamNames import teamDict
from tqdm.notebook import trange, tqdm
from datetime import datetime


### LOGIC

# Get the table
# Go through each row
# If the row has a valid date, then record that date into the dictionary
# in that entry, create another dictionary and populate with the teams and the
# records of those teams

def buildTable(year):
    records = dict()
    url_beg = 'https://www.basketball-reference.com/leagues/NBA_'
    url_middle = '_standings_by_date_'
    url_end = '_conference.html'
    conferences = ['eastern', 'western']
    for conference in conferences:
        records[conference] = dict()
        conference_url = url_beg + str(year) + url_middle + conference + url_end
        response = requests.get(conference_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find(id="standings_by_date")
        rows = table.find_all('tr')
        for row in rows:
        # check if the header is a valid date (otherwise it's a standing or month)
            if(',' in row.th.text):
                date = datetime.strptime(row.th.text, "%b %d, %Y")
                records[conference][date] = dict()
                for standing, data in enumerate(row.find_all('td')):
                    if(data.text):
                        text_split = str.split(data.text)
                        team_abbr = text_split[0]
                        record = text_split[1]
                        if(len(text_split) > 2):
                            tie = text_split[2]
                        else:
                            tie = ''
                        records[conference][date][team_abbr] = dict()
                        records[conference][date][team_abbr]['record'] = record
                        records[conference][date][team_abbr]['tie'] = tie
                        records[conference][date][team_abbr]['standing'] = int(standing) + 1
    return records

def getConferences(year):
    teams = dict()
    url_beg = 'https://www.basketball-reference.com/leagues/NBA_'
    url_end = '_standings.html'
    conferences = [('eastern', 'E'), ('western', 'W')]
    standings_url = url_beg + str(year) + url_end
    response = requests.get(standings_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for conference, conf_url_short in conferences:
        teams[conference] = list()
        id_string = 'divs_standings_' + conf_url_short
        divs_table = soup.find(id=id_string)
        conf_teams = divs_table.tbody.find_all('th', class_='left')
        for team in conf_teams:
            teams[conference].append(team.text.replace("*", ""))
    return teams
