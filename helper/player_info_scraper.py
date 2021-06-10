import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from string import ascii_lowercase
from collections import defaultdict
from Regions import stateDict
from player_table_scraper import player_table_scraper

def player_info_scraper(playerName, playerURL):
    '''
    playerDataScraper scrapes data from each player's specific URL page,
    which contains additional meta-information (e.g. birth place), while
    also containing all stat tables
    '''
    response = requests.get(playerURL)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Meta Info
    birthCity = ''; birthState = ''; birthCountry = ''; shootingHand = ''
    highSchool = ''; highSchoolCity = ''; highSchoolState = ''; highSchoolCountry = ''
    draftTeam = ''; draftRound = 0; draftRoundPick = 0; draftOverallPick = 0
    #Parse out birthCity and birthCountry
    try:
        birthPlace = soup.find(itemprop="birthPlace").get_text()
        birthCity, birthCountry = birthPlace.split(',')
        birthCountry = birthCountry.strip(); birthCity = birthCity.split('in')[1].strip()
        #For US players, birthState column value
        if birthCountry in stateDict.keys():
            birthState = birthCountry
            birthCountry = 'United States of America'
        else:
            pass
    except:
        pass
    meta = soup.find(id='meta')
    try:
        shootingHand = re.findall('<strong>\n  Shoots:\n  </strong>\n  (.*?)\n</p>', str(meta))[0]
    except:
        pass
    for index, i in enumerate(soup.select("strong")):
        if i.get_text(strip=True) == 'High School:':
            high_school_string = i.next_sibling
            high_school_info = i.next_sibling.next_sibling
            highSchool = high_school_string.split(' in ')[0].strip()
            # US Players
            try:
                highSchoolCity = high_school_string.split(' in ')[1].strip()[:-1]
                highSchoolState = re.findall('>(.*?)</a>', str(high_school_info))[0]
                highSchoolCountry = 'United States of America' 
            # International Players
            except:
                highSchoolCity = high_school_string.split(' in ')[1].split(',')[0]
                highSchoolState = 'N/A'
                highSchoolCountry = high_school_string.split()[-1]
        if i.get_text(strip=True) == 'Draft:':
            draftTeam_string = i.next_sibling.next_sibling
            draftInfo_string = i.next_sibling.next_sibling.next_sibling
            try:
                draftTeam = re.findall('>(.*?)</a>', str(draftTeam_string))[0]
            except:
                pass
            draftInfo_uncleaned = re.findall('\d+', draftInfo_string)
            try:
                draftRound = int(draftInfo_uncleaned[0])
                draftRoundPick = int(draftInfo_uncleaned[1])
                draftOverallPick = int(draftInfo_uncleaned[2])
            except:
                pass
    metaInfo = birthCity, birthState, birthCountry, shootingHand, highSchool, highSchoolCity,\
               highSchoolState, highSchoolCountry, draftTeam, draftRound, draftRoundPick,\
               draftOverallPick

    # Statistical Data    
    df_player = player_table_scraper(playerName, soup)
    return metaInfo, df_player