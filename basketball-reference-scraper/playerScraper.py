import re
import requests
from bs4 import BeautifulSoup
from string import ascii_lowercase
from collections import defaultdict
from Regions import stateDict
from PlayerStatObjects import Player, BasicStats, AdvancedStats, ShootingStats, PlayByPlayStats
from tableScraper import tableScraper

def playerDataScraper(playerName, playerURL):
    '''
    playerDataScraper scrapes data from each player's specific URL page,
    which contains additional meta-information (e.g. birth place), while
    also containing all stat tables
    '''
    # playerHash['regular_season' | 'playoffs']['statTable']
    playerHash = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    response = requests.get(playerURL)
    soup = BeautifulSoup(response.text, 'html.parser')

    '''
    Meta Info
    '''
    
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
    
    '''
    Statistical Data
    '''
    
    ## Per Game
    perGame_allFields = ['season', 'age', 'team_id', 'lg_id', 'pos', 'g', 'gs', 'mp_per_g', 'fg_per_g', 'fga_per_g',\
    'fg_pct', 'fg3_per_g', 'fg3a_per_g', 'fg3_pct', 'fg2_per_g', 'fg2a_per_g', 'fg2_pct', 'efg_pct',\
    'ft_per_g', 'fta_per_g', 'ft_pct', 'orb_per_g', 'drb_per_g', 'trb_per_g', 'ast_per_g', 'stl_per_g',\
    'blk_per_g', 'tov_per_g', 'pf_per_g', 'pts_per_g']
    playerHash['regular_season']['per_game'] = tableScraper(perGame_allFields, playerName, soup, 'per_game', 'table')
    playerHash['playoffs']['per_game'] = tableScraper(perGame_allFields, playerName, soup, 'all_playoffs_per_game', 'table')
    
    ## Total
    total_allFields = ['season', 'age', 'team_id', 'lg_id', 'pos', 'g', 'gs', 'mp', 'fg', 'fga',\
    'fg_pct', 'fg3', 'fg3a', 'fg3_pct', 'fg2', 'fg2a', 'fg2_pct', 'efg_pct','ft', 'fta', \
    'ft_pct', 'orb', 'drb', 'trb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts']
    playerHash['regular_season']['total'] = tableScraper(total_allFields, playerName, soup, 'all_totals', 'div')
    playerHash['playoffs']['total'] = tableScraper(total_allFields, playerName, soup, 'all_playoffs_totals', 'div')
    
    ## Per 36
    per36_allFields =  ['season', 'age', 'team_id', 'lg_id', 'pos', 'g', 'gs', 'mp', 'fg_per_mp', 'fga_per_mp',\
    'fg_pct', 'fg3_per_mp', 'fg3a_per_mp', 'fg3_pct', 'fg2_per_mp', 'fg2a_per_mp', 'fg2_pct', 'efg_pct',\
    'ft_per_mp', 'fta_per_mp', 'ft_pct', 'orb_per_mp', 'drb_per_mp', 'trb_per_mp', 'ast_per_mp',\
    'stl_per_mp', 'blk_per_mp', 'tov_per_mp', 'pf_per_mp', 'pts_per_mp']    
    playerHash['regular_season']['per_36'] = tableScraper(per36_allFields, playerName, soup, 'all_per_minute', 'div')
    playerHash['playoffs']['per_36'] = tableScraper(per36_allFields, playerName, soup, 'all_playoffs_per_minute', 'div')
    
    ## Per 100
    per100_allFields =  ['season', 'age', 'team_id', 'lg_id', 'pos', 'g', 'gs', 'mp', 'fg_per_poss', 'fga_per_poss',\
    'fg_pct', 'fg3_per_poss', 'fg3a_per_poss', 'fg3_pct', 'fg2_per_poss', 'fg2a_per_poss', 'fg2_pct', 'efg_pct',\
    'ft_per_poss', 'fta_per_poss', 'ft_pct', 'orb_per_poss', 'drb_per_poss', 'trb_per_poss', 'ast_per_poss',\
    'stl_per_poss', 'blk_per_poss', 'tov_per_poss', 'pf_per_poss', 'pts_per_poss', 'off_rtg', 'def_rtg']
    playerHash['regular_season']['per_100'] = tableScraper(per100_allFields, playerName, soup, 'all_per_poss', 'div')
    playerHash['playoffs']['per_100'] = tableScraper(per100_allFields, playerName, soup, 'all_playoffs_per_poss', 'div')

    ## Advanced
    advanced_allFields =  ['season', 'age', 'team_id', 'lg_id', 'pos', 'g', 'mp', 'per', 'ts_pct', 'fg3a_per_fga_pct',\
    'fta_per_fga_pct', 'orb_pct', 'drb_pct', 'trb_pct', 'ast_pct', 'stl_pct', 'blk_pct', 'tov_pct',\
    'usg_pct', 'ows', 'dws', 'ws', 'ws_per_48', 'obpm', 'dbpm', 'bpm', 'vorp']
    playerHash['regular_season']['advanced'] = tableScraper(advanced_allFields, playerName, soup, 'all_advanced', 'div')
    playerHash['playoffs']['advanced'] = tableScraper(advanced_allFields, playerName, soup, 'all_playoffs_advanced', 'div')
    
    ## Shooting
    shooting_allFields =  ['season', 'age', 'team_id', 'lg_id', 'pos', 'g', 'mp', 'fg_pct', 'avg_dist', 'fg2a_pct_fga', 'pct_fga_00_03',\
    'pct_fga_03_10', 'pct_fga_10_16', 'pct_fga_16_xx', 'fg3a_pct_fga', 'fg2_pct', 'fg_pct_00_03', 'fg_pct_03_10',\
    'fg_pct_10_16', 'fg_pct_16_xx', 'fg3_pct', 'fg2_pct_ast', 'pct_fg2_dunk', 'fg2_dunk', 'fg3_pct_ast', 'pct_fg3a_corner', 'fg3_pct_corner', 'fg3a_heave', 'fg3_heave']
    playerHash['regular_season']['shooting'] = tableScraper(shooting_allFields, playerName, soup, 'all_shooting', 'div')
    playerHash['playoffs']['shooting'] = tableScraper(shooting_allFields, playerName, soup, 'all_playoffs_shooting', 'div')
    
    ## Play-by-Play
    play_allFields = ['season', 'age', 'team_id', 'lg_id', 'pos', 'g', 'mp', 'pct_1', 'pct_2',\
    'pct_3', 'pct_4', 'pct_5', 'plus_minus_on', 'plus_minus_net', 'tov_bad_pass', 'tov_lost_ball',\
    'fouls_shooting', 'fouls_offensive', 'drawn_shooting', 'drawn_offensive', 'astd_pts', 'and1s', 'own_shots_blk']
    playerHash['regular_season']['play-by-play'] = tableScraper(play_allFields, playerName, soup, 'all_pbp', 'div')
    playerHash['playoffs']['play-by-play'] = tableScraper(play_allFields, playerName, soup, 'all_playoffs_pbp', 'div')
    
    return metaInfo, playerHash
