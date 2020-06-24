import re
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from playerScraper import playerDataScraper
from PlayerStatObjects import Player, BasicStats, AdvancedStats, ShootingStats, PlayByPlayStats

def metaInfoScraper(url, playersHash):
    '''
    metaInfoScraper scrapes the meta-data on each player
    '''
    allPlayerCounter = 0; playerDataCounter = 0
    letterPlayerCounter = 0
    draftYear = ''; retireYear = ''; height = 0; weight = 0; birthDate = ''; colleges = ''
    '''
    The API for basketball-reference sorts players by last name first letter 
    (i.e. Kobe Bryant in https://www.basketball-reference.com/players/b/)
    '''
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    '''
    In order to find exactly where all the data is housed, I view the website on 
    Google Chrome and use the developer tools pointer. Here, we can see
    that the tag for the table holding all important data is 'tr'
    For additional help on HTML/tags: https://www.dataquest.io/blog/web-scraping-tutorial-python/
    '''
    playerTableAll = soup.find_all('tr')
    #Header to playerTable is descriptive and not a player -> skip line
    try:
        playerTable = iter(playerTableAll); next(playerTable)
    except:
        return
        
    for index, row in enumerate(playerTable):
        '''
        Once the table is pulled in as playerTable, we'll be using re.findall
        to parse out the text in each field listed below, taking the first element [0]
        given that the results will always be a list with one element, and we 
        want a string to insert as an attribute in the player class
        '''
        playerName = re.findall('.html">(.*?)</a>', str(row))[0]
        draftYear = re.findall('data-stat="year_min">(.*?)</td>', str(row))[0]
        retireYear = re.findall('data-stat="year_max">(.*?)</td>', str(row))[0]
        height = re.findall('data-stat="height">(.*?)</td>', str(row))[0]
        #Converting height from string 'FEET-INCHES' to int INCHES
        try:
            height_split = height.split('-'); height = int(height_split[0])*12 + int(height_split[1])
        except:
            pass
        #Converting weight from string to int
        weight = re.findall('data-stat="weight">(.*?)</td>', str(row))[0]
        try:
            weight = int(weight)
        except:
            pass
        birthDate = re.findall('data-stat="birth_date">(.*?)</td>', str(row))
        #Some players do not have birthdates listed
        try:
            birthDate = re.findall('>(.*?)</a>', str(birthDate))[0]
        except:
            birthDate = ''
        colleges = re.findall('data-stat="colleges">(.*?)</td>', str(row))
        #Same with colleges not being listed for some of the early players
        try:
            colleges = re.findall('>(.*?)</a>', str(colleges))[0]
        except:
            colleges = ''
        #playerURL will lead us to each player's own page, which contains the trove
        #of statistics that we will use in future analyses
        playerURL = re.findall('a href="(.*?)">', str(row))
        playerURL = 'https://www.basketball-reference.com' + playerURL[0]
        playerOverview = playerName, draftYear, retireYear, height, weight, birthDate, colleges, playerURL
        
        '''Running playerDataScraper to capture playerData'''
        playerData, playerHash = playerDataScraper(playerName, playerURL)
        
        '''Creating Player object and inserting to playerHash'''
        allPlayerInfo = playerOverview + playerData
        playerObject = Player(allPlayerInfo)
        playersHash[playerName]['meta_info'] = playerObject
        playersHash[playerName]['stats'] = playerHash
        letterPlayerCounter += 1; allPlayerCounter += 1; playerDataCounter += 20
    print ('      \'' + url[-1] + '\' Players Captured: ', letterPlayerCounter)
    return playersHash

    