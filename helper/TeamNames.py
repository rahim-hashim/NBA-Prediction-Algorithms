#!/usr/bin/python
import sys
import re

teamDict = {
        'ATL':	'Atlanta Hawks',
        'BKN':	'Brooklyn Nets',
        'BK' :  'Brooklyn Nets',
        'BRK':  'Brooklyn Nets',
        'BOS':	'Boston Celtics',
        'CHA':	'Charlotte Hornets',
        'CHO':  'Charlotte Hornets',
        'CHI':	'Chicago Bulls',
        'CLE':	'Cleveland Cavaliers',
        'DAL':	'Dallas Mavericks',
        'DEN':	'Denver Nuggets',
        'DET':	'Detroit Pistons',
        'GSW':	'Golden State Warriors',
        'GS':   'Golden State Warriors',
        'HOU':	'Houston Rockets',
        'IND':	'Indiana Pacers',
        'LAC':	'Los Angeles Clippers',
        'LAL':	'Los Angeles Lakers',
        'MEM':	'Memphis Grizzlies',
        'MIA':	'Miami Heat',
        'MIL':	'Milwaukee Bucks',
        'MIN':	'Minnesota Timberwolves',
        'NOP':	'New Orleans Pelicans',
        'NYK':	'New York Knicks',
        'OKC':	'Oklahoma City Thunder',
        'ORL':	'Orlando Magic',
        'PHI':	'Philadelphia 76ers',
        'PHX':	'Phoenix Suns',
        'PHO':  'Phoenix Suns',
        'POR':	'Portland Trail Blazers',
        'SAC':	'Sacramento Kings',
        'SAS':	'San Antonio Spurs',
        'TOR':	'Toronto Raptors',
        'UTA':	'Utah Jazz',
        'WAS':	'Washington Wizards'}

coversNames = {
        'BN' : 'BRK',
        'BK' : 'BRK',
        'BKN': 'BRK',
        'CHA': 'CHO',
        'GS': 'GSW',
        'NO': 'NOP',
        'NY': 'NYK',
        'PHX' : 'PHO',
        'SA': 'SAS'
}
