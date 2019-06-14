""" Script that creates additional table that stores info about goal and shots for players trios. Created table is used for further search.
    Running this may take a while.
"""
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import sqlite3
import xml.etree.ElementTree as ET
import trio_stat # db table for stroring trio stats

"""Return attributes for player with given api_id ordered by date"""
def players_attributes(pl_api_id, curs):
    # curs.execute(
    #     'select date player_fifa_api_id, player_api_id, overall_rating, crossing, finishing, heading_accuracy, short_passing,' +
    #     ' volleys, dribbling, curve, free_kick_accuracy, long_passing, ball_control, acceleration, sprint_speed,agility, reactions, balance, ' +
    #     'shot_power, jumping, stamina,strength, long_shots, aggression, interceptions, positioning,vision, penalties, marking, standing_tackle, sliding_tackle' +
    #     ' from Player_Attributes where player_api_id = ' + str(pl_api_id) + ' order by date;')

    curs.execute('select date, player_fifa_api_id, crossing, finishing, short_passing, volleys, dribbling, free_kick_accuracy, long_passing, ball_control, shot_power, long_shots, interceptions, positioning, vision, standing_tackle, sliding_tackle' +
        ' from Player_Attributes where player_api_id = ' + str(pl_api_id) + ' order by date;')
    return curs.fetchall()

"""Return players attributes for given date sorted"""
def player_attribute_at_date(pl_api_id, date, curs):
    # curs.execute(
    #     'select date player_fifa_api_id, player_api_id, overall_rating, crossing, finishing, heading_accuracy, short_passing,' +
    #     ' volleys, dribbling, curve, free_kick_accuracy, long_passing, ball_control, acceleration, sprint_speed,agility, reactions, balance, ' +
    #     'shot_power, jumping, stamina,strength, long_shots, aggression, interceptions, positioning,vision, penalties, marking, standing_tackle, sliding_tackle' +
    #     ' from Player_Attributes where player_api_id = ' + str(pl_api_id) + " and date <= '"+str(date)+"';")
    curs.execute(
        'select date, player_fifa_api_id, crossing, finishing, short_passing, volleys, dribbling, free_kick_accuracy, long_passing, ball_control, shot_power, long_shots, interceptions, positioning, vision, standing_tackle, sliding_tackle' +
        ' from Player_Attributes where player_api_id = ' + str(pl_api_id) + " and date <= '" + str(date) + "';")

    return curs.fetchall()[-1]

"""Return matches for given player that took place from from_date to to_date"""
def players_matches(pl_api_id, from_date, to_date, curs):
    curs.execute("select * from Match where (goal not null or shoton not null) and date between '"+str(from_date)+ "' and '" +str(to_date)+ "' and  "+
                 str(pl_api_id)+' in (away_player_1, away_player_2, away_player_3, away_player_4, away_player_5, away_player_6,away_player_7,away_player_8,away_player_9, away_player_10, away_player_11,'+
                 'home_player_1, home_player_2, home_player_3, home_player_4, home_player_5, home_player_6,home_player_7,home_player_8,home_player_9, home_player_10, home_player_11); ')
    return curs.fetchall()

"""Returns 2-elements list with api_ids of players that played alongside given player in given match"""
def players_offensive_partners(pl_api_id, match):
    """
        COL              match - index
    home_player_Y1   ==>  33
    home_player_Y11  ==>  43

    away_player_Y1   ==>  44
    away_player_Y11  ==>  54

    home_player_1    ==>  55
    home_player_11   ==>  65

    away_player_1    ==>  66
    away_player_11   ==>  76
    """
    y_beg = 33
    y_end = 43
    team_beg = 55
    team_end = 65
    if pl_api_id in match[66:76]:
        y_beg = 44
        y_end = 54
        team_beg = 66
        team_end = 76
    pl_nums = [] #numbers of players with biggest Ys values spotted so far y[0] >= y[1]
    for y_i in range(y_beg, y_end+1):
        if len(pl_nums) == 2:
            break
        if match[y_i] is not None:
            pl_nums.append(y_i)
    if len(pl_nums) < 2:
        return None
    n0 = pl_nums[0]
    n1 = pl_nums[1]    
    if match[n1] > match[n0]: #swap pl_nums to maintain assumed order
        pl_nums = [n1, n0]
    for i in range(y_beg+2,y_end+1):
        if (match[team_beg+(i - y_beg)] in [None, api_id]) or (match[i] is None):
            continue
        if match[i] >= match[pl_nums[0]]:
            pl_nums = [i, pl_nums[0]]
        elif match[i] > match[pl_nums[1]]:
            pl_nums[1] = i

    return [
            match[team_beg+(pl_nums[0]-y_beg)],
            match[team_beg+(pl_nums[1]-y_beg)] ] # return ids of players with biggest Y values


"""Returns XML with goals info"""
def match_goals(match):
    return match[77]

"""Returns XML with shots info"""
def match_shots(match):
    return match[78]

"""Returns number of goals that  player with player_id scored
goalsXML is an XML stored in Match goal """
def goals_for_player(goalXML, player_id):
    if goalXML is None:
        return 0
    gt = ET.fromstring(goalXML)
    goals_scored = 0
    for v in gt.findall('value'):
        if v.find('player1') is None or v.find('stats') is None or v.find('stats').find('goals') is None:
            continue
        if int(v.find('player1').text) == player_id:
            goals_scored += int(v.find('stats').find('goals').text)
    return goals_scored

"""Returns shots of a player with player_id
shotsXML is an XML stored in Match shoton """
def shots_for_player(shotXML, player_id):
    if shotXML is None:
        return 0
    st = ET.fromstring(shotXML)
    shots = 0
    for v in st.findall('value'):
        if v.find('player1') is None:
            continue
        if int(v.find('player1').text) == player_id:
            shots += 1
    return shots



path = 'input/'  #Insert path here
database = path + 'database.sqlite'
conn = sqlite3.connect(database)
c = conn.cursor()

trio_stat.create_table(conn) # create table that stores offensive trios goals and shots for convinient lookup

#Prepare info about trios shots and goals
c.execute('SELECT * FROM  Player')
players = c.fetchall()
counter = 0
players_total = len(players)
for player in players:
    counter += 1
    print("Player ",counter," of ",players_total)
    api_id = player[1]
    #select all attributes for given player and order it by date - date is important for further games selection
    attributes = players_attributes(api_id, c)
    for i in range(0, len(attributes)):
        attr = attributes[i]
        attr_date  = attr[1]
        next_attr_date = "2199-12-31 23:59:59"
        if i < (len(attributes)-1): # attributes are ordered by date
            next_attr_date = attributes[i+1][1]
        games = players_matches(api_id, attr_date, next_attr_date, c)
        # TODO odczytac gole i strzaly z meczow i utworzyc mape
        for game in games:
            goals = goals_for_player(match_goals(game), api_id)
            shots = shots_for_player(match_shots(game), api_id)
            if( (goals == 0 and shots==0) or (game[5] is None)): #game[5] is date
                continue

            partners_ids = players_offensive_partners(api_id, game)
            if partners_ids is None:
                continue
            # p1_attr = player_attribute_at_date(partners_ids[0],game[5],c)[2:] # game[5] is date
            # p2_attr = player_attribute_at_date(partners_ids[1], game[5],c)[2:]  # game[5] is date
            # if trio_stats.get(attr) is None:
            #     stat_tup = (goals,shots,p1_attr, p2_attr)
            #     trio_stats[ attr[2:] ] = [stat_tup]
            # else:
            #     found = False
            #     for stat in trio_stats[attr[2:]]:
            #         if(p1_attr == stat[2] and p2_attr == stat[3]): # update existing tuple
            #             stat[0] += goals
            #             stat[1] += shots
            #             found = True
            #             break
            #     if not found:
            #         trio_stats.append( (goals, shots, p1_attr, p2_attr) ) #add new touple to list
            player1 = attr[2:]
            player2 = player_attribute_at_date(partners_ids[0],game[5],c)[2:] # game[5] is date
            player3 = player_attribute_at_date(partners_ids[1], game[5],c)[2:]  # game[5] is date
            if(None in player1 or None in player2 or None in player3): # ignore players with incomplete attributes
                continue
            
            stats = trio_stat.trio_stats(player1, player2, player3,c)
            if stats is None:
                trio_stat.insert_trio_stat(c, goals, shots, player1, player2, player3)  
            else: # upadte existing row
                trio_stat.id_increment_goals_and_shots(goals, shots, stats[0], c)

c.execute("commit;")













