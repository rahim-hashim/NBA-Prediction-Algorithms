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

class BasicStats():
    '''
    BasicStats object contains all basic statistics 
    (e.g. Points, Assists, Steals)
    '''
    def __init__(self, SeasonData):
        
        #The "Per 100 Possessions" Table has 2 more fields (Offensive Rating, Defensive Rating) than other
        #BasicStats Tables ("Per Game", "Per 36 Minutes")
        nonPossData = False
        if len(SeasonData) == 31:
            nonPossData = True
        if nonPossData:
            name, season, age, team_id, lg_id, pos, g, gs, mp, fg, fga,\
            fg_pct, fg3, fg3a, fg3_pct, fg2, fg2a, fg2_pct,\
            efg_pct, ft, fta, ft_pct, orb, drb, trb,\
            ast, stl, blk, tov, pf, pts = SeasonData  
        else:
            name, season, age, team_id, lg_id, pos, g, gs, mp, fg, fga,\
            fg_pct, fg3, fg3a, fg3_pct, fg2, fg2a, fg2_pct,\
            efg_pct, ft, fta, ft_pct, orb, drb, trb,\
            ast, stl, blk, tov, pf, pts, off_rtg, def_rtg = SeasonData              
            
        self.name = name
        self.season = season
        self.age = age
        self.team_id = team_id
        self.lg_id = lg_id
        self.pos = pos
        self.g = g
        self.gs = gs
        self.mp = mp
        self.fg = fg
        self.fga = fga
        self.fg_pct = fg_pct
        self.fg3 = fg3a
        self.fg3a = fg3a
        self.fg3_pct = fg3_pct
        self.fg2 = fg2
        self.fg2a = fg2a
        self.fg2_pct = fg2_pct
        self.efg_pct = efg_pct
        self.ft = ft
        self.fta = fta
        self.ft_pct = ft_pct
        self.orb = orb
        self.drb = drb
        self.trb = trb
        self.ast = ast
        self.stl = stl
        self.blk = blk
        self.tov = tov
        self.pf = pf
        self.pts = pts
        
        if not nonPossData:
            self.off_rtg = off_rtg
            self.def_rtg = def_rtg
            
class AdvancedStats():
    '''
    AdvancedStats object contains all advanced statistics 
    (e.g. True Shooting, Win Share, VORP)
    '''
    def __init__(self, SeasonData):
        name, season, age, team_id, lg_id, pos, g, mp, per, ts_pct,\
        par3, ftr, orb_pct, drb_pct, trb_pct, ast_pct, stl_pct, blk_pct,\
        tov_pct, usg_pct, ows, dws, ws, ws_48, obpm, dbpm, bpm, vorp = SeasonData  
        
        self.name = name
        self.season = season
        self.age = age
        self.team_id = team_id
        self.lg_id = lg_id
        self.pos = pos
        self.g = g
        self.mp = mp
        self.per = per
        self.ts_pct = ts_pct
        self.par3 = par3
        self.ftr = ftr
        self.orb_pct = orb_pct
        self.drb_pct = drb_pct
        self.trb_pct = trb_pct
        self.ast_pct = ast_pct
        self.stl_pct = stl_pct
        self.blk_pct = blk_pct
        self.tov_pct = tov_pct
        self.usg_pct = usg_pct
        self.ows = ows
        self.dws = dws
        self.ws = ws
        self.ws_48 = ws_48
        self.obpm = obpm
        self.dbpm = dbpm
        self.bpm = bpm
        self.vorp = vorp
        
class ShootingStats():
    '''
    ShootingStats object contains all shooting-specific statistics 
    (e.g. Average Distance, FG % within 3ft, Dunks)
    '''
    def __init__(self, SeasonData):
        name, season, age, team_id, lg_id, pos, g, mp, fg_pct, avg_dist, fg2a_pct_fga,\
        pct_fga_00_03, pct_fga_03_10, pct_fga_10_16, pct_fga_16_xx, fg3a_pct_fga,\
        fg2_pct, fg_pct_00_03, fg_pct_03_10, fg_pct_10_16, fg_pct_16_xx, fg3_pct,\
        fg2_pct_ast, pct_fg2_dunk, fg2_dunk, fg3_pct_ast, pct_fg3a_corner,\
        fg3_pct_corner, fg3a_heave, fg3_heave = SeasonData  
        
        self.name = name
        self.season = season
        self.age = age
        self.team_id = team_id
        self.lg_id = lg_id
        self.pos = pos
        self.g = g
        self.mp = mp
        self.fg_pct = fg_pct
        self.avg_dist = avg_dist
        self.fg2a_pct_fga = fg2a_pct_fga
        self.pct_fga_00_03 = pct_fga_00_03
        self.pct_fga_03_10 = pct_fga_03_10
        self.pct_fga_10_16 = pct_fga_10_16
        self.pct_fga_16_xx = pct_fga_16_xx
        self.fg3a_pct_fga = fg3a_pct_fga
        self.fg2_pct = fg2_pct
        self.fg_pct_00_03 = fg_pct_00_03
        self.fg_pct_03_10 = fg_pct_03_10
        self.fg_pct_10_16 = fg_pct_10_16
        self.fg_pct_16_xx = fg_pct_16_xx
        self.fg3_pct = fg3_pct
        self.fg2_pct_ast = fg2_pct_ast
        self.pct_fg2_dunk = pct_fg2_dunk
        self.fg2_dunk = fg2_dunk
        self.fg3_pct_ast = fg3_pct_ast
        self.pct_fg3a_corner = pct_fg3a_corner
        self.fg3_pct_corner = fg3_pct_corner
        self.fg3a_heave = fg3a_heave
        self.fg3_heave = fg3_heave

class PlayByPlayStats():
    '''
    PlayByPlayStats object contains all play-by-play statistics 
    (e.g. Plus Minus On/Net, And1s, Drawn Fouls)
    '''
    def __init__(self, SeasonData):
        name, season, age, team_id, lg_id, pos, g, mp, pct_1, pct_2,\
        pct_3, pct_4, pct_5, plus_minus_on, plus_minus_net, tov_bad_pass,\
        tov_lost_ball, fouls_shooting, fouls_offensive, drawn_shooting,\
        drawn_offensive, astd_pts, and1s, own_shots_blk = SeasonData
        
        self.name = name
        self.season = season
        self.age = age
        self.team_id = team_id
        self.lg_id = lg_id
        self.pos = pos
        self.g = g
        self.mp = mp
        self.pct_1 = pct_1
        self.pct_2 = pct_2
        self.pct_3 = pct_3
        self.pct_4 = pct_4
        self.pct_5 = pct_5
        self.plus_minus_on = plus_minus_on
        self.plus_minus_net = plus_minus_net
        self.tov_bad_pass = tov_bad_pass
        self.tov_lost_ball = tov_lost_ball
        self.fouls_shooting = fouls_shooting
        self.fouls_offensive = fouls_offensive
        self.drawn_shooting = drawn_shooting
        self.drawn_offensive = drawn_offensive
        self.astd_pts = astd_pts
        self.and1s = and1s
        self.own_shots_blk = own_shots_blk