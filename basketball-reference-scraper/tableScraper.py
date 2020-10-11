import re
import os
import sys
import time
import pandas as pd
from bs4 import BeautifulSoup
from string import ascii_lowercase
from collections import defaultdict

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
            seasonCol = re.findall('<(.*?)th>', str(row))[0]
            if 'Career' in str(seasonCol):
                season = ['Career']
            elif '-' in str(seasonCol):
                seasonSplit = seasonCol.split('-')
                if len(seasonSplit) == 3:
                    season = [seasonSplit[1][-4:] + '-' + seasonSplit[2][:2]]
                else:
                    #ignoring non-year / non-career listings (i.e. team-specific stats)
                    continue
            row1 = BeautifulSoup(row, 'html.parser')
            dataCols = row1.find_all('td'); data = [ele.text.strip() for ele in dataCols]
            statData = season + data
            statData = fieldsCheck(allFields, statFields, statData)
            statData = [playerName] + statData
            finalFields = ['player_name'] + allFields
            for f_index, field in enumerate(finalFields):
                statHash[field] = statData[f_index]
            df = pd.DataFrame([statHash])
            print(df.head())
        return statHash
    else:
        return
        blankSpots = len(allFields)-1
        blankArrays = ([''] * blankSpots)
        statData = [playerName, 'Career'] + blankArrays
