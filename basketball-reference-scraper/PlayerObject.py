#!/usr/bin/python
import sys
import re

# Class Instantiation
### Called within basketballReference to instantiate class objects and attributes

class Player():
    '''
    Player object contains all meta-data for each player, including biostats, 
    background, and draft information
    '''
    def __init__(self, metaInfo):
        name, draftYear, retireYear, height, weight, birth_date, colleges, url,\
        birthCity, birthState, birthCountry, shootingHand, highSchool, highSchoolCity,\
        highSchoolState, highSchoolCountry, draftTeam, draftRound, draftRoundPick,\
        draftOverallPick = metaInfo 
        
        self.name = name
        self.draftYear = draftYear
        self.retireYear = retireYear
        self.height = height
        self.weight = weight
        self.birth_date = birth_date
        self.colleges = colleges
        self.url = url
        self.birthCity = birthCity
        self.birthState = birthState
        self.birthCountry = birthCountry
        self.shootingHand = shootingHand
        self.highSchool = highSchool
        self.highSchoolCity = highSchoolCity
        self.highSchoolState = highSchoolState
        self.highSchoolCountry = highSchoolCountry
        self.draftTeam = draftTeam
        self.draftRound = draftRound
        self.draftRound_pick = draftRoundPick
        self.draftOverallPick = draftOverallPick