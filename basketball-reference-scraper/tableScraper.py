import re
import os
import sys
import time
from bs4 import BeautifulSoup
from string import ascii_lowercase
from collections import defaultdict
from PlayerStatObjects import Player, BasicStats, AdvancedStats, ShootingStats, PlayByPlayStats

def fieldsCheck(allFields, someFields, data):
    '''
    fieldsCheck compares the provided fields (allFields) with the 
    scraped fields (someFields), in the case where certain player tables
    don't have all the same columns.
    '''
    emptyIndex = []
    someFieldsCopy = someFields[:]
    for index in range(len(someFieldsCopy)):
        if someFieldsCopy[index] == '' or '-dum' in someFieldsCopy[index]:
            emptyIndex.append(index)
    for index in sorted(emptyIndex, reverse=True):
        del someFieldsCopy[index]
        del data[index]
    for index, field in enumerate(allFields):
        try:
            if field != someFieldsCopy[index]:
                someFieldsCopy.insert(index, field)
                data.insert(index, '')
        except IndexError:
            someFieldsCopy.insert(index, field)
            data.insert(index, '')
    return data

def tableScraper(allFields, playerName, playerSoup, statType, statTag):
    '''
    tableGeneralScraper will be used to scrape all table types to insert into
    statHash. Given the generalizable nature of the html structure on each player's
    page, the location of the data is the same, with the only key differences being 
    the tables tag (statTag) and column names for each (statType).
    '''
    statHash = defaultdict(dict)
    
    table = playerSoup.find(lambda tag: tag.name==statTag and tag.has_attr('id') and tag['id']==statType)
    rows = re.findall('<tr(.*?)</tr>', str(table))
    statFields = []
    if rows:
        for index, row in enumerate(rows):
            if index == 0:
                statFields = re.findall('data-stat="(.*?)"', str(row))
                if 'DUMMY' in statFields:
                    statFields = list(filter(lambda x: x != 'DUMMY', statFields)) # removes blank columns labeled as 'DUMMY'
            seasonCol = re.findall('<(.*?)th>', str(row))[0]
            if 'Career' in str(seasonCol):
                season = ['Career']
            elif '-' in str(seasonCol):
                seasonSplit = seasonCol.split('-')
                if len(seasonSplit) == 3:
                    season = [seasonSplit[1][-4:] + '-' + seasonSplit[2][:2]]
                else:
                    #ignoring non-year / non-career listings
                    continue
            row1 = BeautifulSoup(row, 'html.parser')
            dataCols = row1.find_all('td'); data = [ele.text.strip() for ele in dataCols]
            if 'DUMMY' in dataCols:
                dataCols = list(filter(lambda x: x != 'DUMMY', dataCols)) # removes blank columns labeled as 'DUMMY'
            statData = season + data
            statData = fieldsCheck(allFields, statFields, statData)
            statData = [playerName] + statData
            if season and ('-' in str(season) or 'Career' in str(season)):
                if 'per_game' in statType or 'total' in statType\
                or 'per_minute' in statType or 'per_poss' in statType:
                    statsObject = BasicStats(statData)
                elif 'advanced' in statType:
                    statsObject = AdvancedStats(statData)
                elif 'shooting' in statType:
                    statsObject = ShootingStats(statData)
                elif 'pbp' in statType:
                    statsObject = PlayByPlayStats(statData)
                season = str(season[0])
                statHash[season] = statsObject
        return statHash
    else:
        return
        blankSpots = len(allFields)-1
        blankArrays = ([''] * blankSpots)
        statData = [playerName, 'Career'] + blankArrays
        if 'per_game' in statType or 'total' in statType\
        or 'per_minute' in statType or 'per_poss' in statType:
            statsObject = BasicStats(statData)
        elif 'advanced' in statType:
            statsObject = AdvancedStats(statData)
        elif 'shooting' in statType:
            statsObject = ShootingStats(statData)
        elif 'play' in statType:
            statsObject = PlayByPlayStats(statData)
