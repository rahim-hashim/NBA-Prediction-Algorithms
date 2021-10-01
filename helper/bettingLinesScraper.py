# bettingLinesScraper.py
# Aunoy Poddar
# 6_30_2020
# Scraping the betting lines from cover.com for NBA Predictions
# with Rahim Hashim.

import re
import sys
import requests
from bs4 import BeautifulSoup
from string import ascii_lowercase
from collections import defaultdict
from itertools import zip_longest
from TeamNames import teamDict, coversNames
from tqdm.notebook import trange, tqdm
from datetime import datetime
from recordDateScraper import buildTable, getConferences

def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def getDate(text, ref_date, year):
    date = datetime.strptime(text + ' 2000', '%b %d %Y') # This is for leap year
    #date = date.replace(year=year)
    if date < ref_date:
        date = date.replace(year=(year + 1))
    else:
        date = date.replace(year = year)
    
    return date

def getHomeAway(text, TEAM_NAME):
    at_char = '@' in text
    OPP_STRING = text if not at_char else text.replace("@", "").strip()
    OPP_NAMES = OPP_STRING.split()
    OPP_NAME = OPP_NAMES[0]

    away = TEAM_NAME if at_char else OPP_NAME
    home = OPP_NAME if at_char else TEAM_NAME

    return home, away

def getScore(text, isHome):
    OT = 'OT' in text
    text = text.replace("L", "").strip() if 'L' in text else text.replace("W", "").strip()
    scores = text.split('-')
    home_score = scores[1-isHome]; away_score = scores[isHome]
    return home_score, away_score, OT

def getSpread(text, isHome):
    ATS = ['L', 'W', 'P']
    for ats in ATS:
        text = text.replace(ats, "").strip()
    return (isHome*2 - 1) * float(text)

def getConferenceHelper(team_full, conf_list):
    team_conf = 'eastern' if team_full in conf_list['eastern'] else ""
    if(not team_conf):
        team_conf = 'western' if team_full in conf_list['western'] else ""
    if(not team_conf):
        sys.exit('Conference Helper could not locate team in NBA reference table: ' +
                   team_full)
    return team_conf

def getConference(home, away, conf_list):
    home_full = teamDict[home]; away_full = teamDict[away]
    home_conf = getConferenceHelper(home_full, conf_list)
    away_conf = getConferenceHelper(away_full, conf_list)
    return home_conf, away_conf

def standardize_names(home, away):
    home_name = home if home not in coversNames.keys() else coversNames[home]
    away_name = away if away not in coversNames.keys() else coversNames[away]
    return home_name, away_name

def bettingLinesScraper(team_url, team_name, year, season_specs, records, conf_list, meta_list):

    response = requests.get(team_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    games = []; new_meta = []
    ref_date = datetime(2000, 8, 1)

    # Always have the spread for the Home team, against the spread
    # Do not include Over Under for now
    keys = ['Date', 'Home_Team', 'Away_Team', 'Home_Score',
            'Away_Score', 'Spread', 'Home_Record', 'Away_Record',
            'Home_Standing', 'Away_Standing']
    NUM_TABLE_ENTRIES = 5

    #### NEED TO GET TEAM NAME SOMEHOW
    TEAM_NAME = team_name

    ### Check if team made playoffs
    made_playoffs = False
    table_headers = soup.find_all('h2')
    for th in table_headers:
        if th.contents[0].strip() == "Playoffs":
            made_playoffs = True

    game_types = ['Playoffs', 'Regular Season'] if made_playoffs else ['Regular Season']
    
    tables = soup.find_all('table')
    table_ind = 0
    
    for table in tables:
        ### Skip the process if table is not included in game type (reg season or playoffs)
        ### Pick the past results page tables for playoffs and reg season
        ### tables is reversed because it is then goes chronologically
        if 'covers-CoversResults-Table' in table['class'] and len(table['class']) == 3:
            table_entries = grouper(table.find_all('td'), NUM_TABLE_ENTRIES)
            
            # skip if already done
            if game_types[table_ind] not in season_specs:
                table_ind = table_ind + 1
                continue 
            else:
                table_ind = table_ind + 1
            for entry in table_entries:
		# Initialize game dictionary
                game = dict.fromkeys(keys)
		# Scrape Date
                date = getDate(entry[0].text.strip(), ref_date, year)
                game['Date'] = date
		# Scrape Home Team and Away Team
                covers_home, covers_away = getHomeAway(entry[1].text.strip(), TEAM_NAME)
                home, away = standardize_names(covers_home, covers_away)
                game['Home_Team'] = home; game['Away_Team'] = away
		# Scrape Scores and OT info
                home_score, away_score, OT = getScore(entry[2].text.strip(),
                        TEAM_NAME == game['Home_Team'])
                game['Home_Score'] = home_score; game['Away_Score'] = away_score
		# Scrape ATS and Spread (Right now, the home team spread will be shown)
                spread = getSpread(entry[3].text.strip(), TEAM_NAME == game['Home_Team'])
                game['Spread'] = spread
                game_meta =  (date, home, away) 
                if game_meta not in meta_list:
                    games.append(game); new_meta.append(game_meta)
        # Scrape Record
                home_conf, away_conf = getConference(home, away, conf_list)
                game['Home_Record'] = records[home_conf][date][home]['record']
                game['Away_Record'] = records[away_conf][date][away]['record']
                game['Home_Standing'] = str(records[home_conf][date][home]['standing']) + \
                                        records[home_conf][date][home]['tie']
                game['Away_Standing'] = str(records[away_conf][date][away]['standing']) + \
                                        records[away_conf][date][away]['tie']
    return games, new_meta

def scrape(start_year, end_year):

    # List of games, each game is a dictionary object
    # List of meta information to avoid multiple additions
    games = []
    meta = []
    url = 'https://www.covers.com/sport/basketball/nba/teams/main/'
    
    game_types = { 'R': ['Regular Season'],
                   'P': ['Playoffs'],
                   'B': ['Regular Season', 'Playoffs']}
                   
    #start_year_input = input('\nInput starting year of season that you want ' +
    #                    'to start scraping from  (e.g. 2015 if start at 2015): ')
    #end_year_input = input('\nInput ending year of season that you want to ' +
    #                    'end scraping at (e.g. 2017 if scraping 2015-2016' +
    #                    'and 2016-2017 season')
    #try:
    #    start_year = int(start_year_input)
    #    end_year = int(end_year_input)
    #except:
    #    sys.exit('Invalid Year')
    specs = 'R'
    #specs = input('\nScrape Regular Season (R), Playoff Games (P), or both (B): (default R)')
    #specs= 'R' if specs== '' else specs
    if specs not in game_types.keys():
        sys.exit('Invalid Game Specs')
        
    for year in trange(start_year, end_year, desc = 'Years', leave = True):
        t = tqdm(teamDict.keys(), desc = 'Teams', leave = False)
        print('Initializing Records for ' + str(year) + '...')
        records = buildTable(year+1)
        print('Getting conference lists ...')
        conference_list = getConferences(year+1)
        for team_abbr in t:
            t.set_description(team_abbr)
            t.refresh()
            team_name = teamDict[team_abbr].lower()
            team_url = url + team_name.replace(" ", "-") + \
                    '/' + str(year) + '-' + str(year+1)
        # Send in built table for record scraping
            add_games, add_meta = bettingLinesScraper(team_url, team_abbr,
                                  year, game_types[specs], records,
                                  conference_list, meta)

            games = games + add_games; meta = meta + add_meta
    return games