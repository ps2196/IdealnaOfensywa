""" Convenience queries for trio_stat table """

import sqlite3 

attr_columns = ['crossing', 'finishing', 'short_passing', 'volleys', 'dribbling', 'free_kick_accuracy','long_passing','ball_control', 'shot_power', 'long_shots', 'interceptions', 'positioning', 'vision', 'standing_tackle', 'sliding_tackle']
TOLERANCE_W  = [   2.5,        1,             2,          30,         10,              30,                 2.5,           1,             1.3,          3,           80,             1,             5,         80,                    80      ] 
#TOLERANCE_W = [1 for _ in range(0, len(attr_columns))]
PLAYER_1_ATTR_BEG = 3 
PLAYER_1_ATTR_END = PLAYER_1_ATTR_BEG+len(attr_columns)
PLAYER_2_ATTR_BEG = PLAYER_1_ATTR_END
PLAYER_2_ATTR_END = PLAYER_2_ATTR_BEG+len(attr_columns)
PLAYER_3_ATTR_BEG = PLAYER_2_ATTR_END+1
PLAYER_3_ATTR_END = PLAYER_3_ATTR_BEG+len(attr_columns)

#TOLERANCE_W = [1.5, 1, 1.3, 1.3, 1, 1, 1.5, 1, 1.3, 1.2, 90, 1, 1, 90, 90]
#TOLERANCE_W = [1.5, 1, 1.3, 1.3, 1, 1, 1.5, 1, 1.3, 1.2, 90, 1, 1, 90, 90] # tolerance weights for attributes

"""Return string cotaining columns definition for CREATE TABLE satement"""
def attr_col_names_with_type(col_sufix=""):
    s = ""
    for attr in attr_columns[:-1]:
        s+=attr+col_sufix+" integer NOT NULL, "
    s+=attr_columns[-1]+col_sufix+" integer NOT NULL"
    return s
    
def trio_stat_columns_str(sufixes):
    cols = ""
    for sufix in sufixes:
        for attr in attr_columns:
            cols+=attr+sufix+', '
    return cols[:-2] # trunc ', ' at the end

PLAYER_1_ATTRS = trio_stat_columns_str(['_1'])
PLAYER_2_ATTRS = trio_stat_columns_str(['_2'])
PLAYER_3_ATTRS = trio_stat_columns_str(['_3'])

def player_to_string(player):
    s = ""
    for attr in player[:-1]:
        s += str(attr) +", "
    s += str(player[-1])
    return s
    
"""Return string forrmatted like <attr_name> = value and ... to be used where clause """
def player_atrr_cmp_str(player, sufix, tol=0):
    s = "("
    if tol == 0:
        for i in range(0, len(attr_columns)): 
            tolerance = tol * TOLERANCE_W[i]
            s += attr_columns[i]+sufix+' = '+str(player[i]+tolerance)+" and "
        s+=attr_columns[-1]+sufix+' = '+str(player[-1]+(tolerance * TOLERANCE_W[-1]))+')'
    else:
        for i in range(0, len(attr_columns)): 
            tolerance = tol * TOLERANCE_W[i]
            s += attr_columns[i]+sufix+' between '+str(player[i]-tolerance)+' and '+str(player[i]+tolerance) +" and "
        tolerance = tol * TOLERANCE_W[-1]
        s+=attr_columns[-1]+sufix+' between '+str(player[-1]-tolerance)+' and '+str(player[-1]+tolerance)+' )'
    return s

"""Return where clause for select where player2 and player3 order doesn't matter"""
def partners_query_condition(player2, player3, tol=0):
    s = "( "
    if tol == 0: # use = 
        for i in range(0, len(attr_columns)):
            s += attr_columns[i]+'_2 = '+str(player2[i])+' and '
        s += attr_columns[-1]+'_2 = '+str(player2[-1])+' ) or ( '
        #player3
        for i in range(0, len(attr_columns)):
            s += attr_columns[i]+'_3 = '+str(player3[i])+' and '
        s += attr_columns[-1]+'_3 = '+str(player3[-1])+')'    
    else: #use between clause in query
        #player2
        for i in range(0, len(attr_columns)):
            tolerance = tol * TOLERANCE_W[i]
            s += attr_columns[i]+'_2 between '+str(player2[i] - tolerance)+' and '+str(player2[i] + tolerance)+' and '
        tolerance = tol * TOLERANCE_W[-1]
        s += attr_columns[-1]+'_2 between '+str(player2[-1] - tolerance)+' and '+str(player2[-1]+tolerance)+' ) or ('
        #player3
        for i in range(0, len(attr_columns)):
            tolerance = tol * TOLERANCE_W[i]
            s += attr_columns[i]+'_3 between '+str(player3[i] - tolerance)+' and '+str(player3[i] + tolerance)+' and '
        tolerance = tol * TOLERANCE_W[-1]
        s += attr_columns[-1]+'_3 between '+str(player3[-1] - tolerance)+' and '+str(player3[-1] + tolerance)+')'
    return s

"""Create table Trio_Stat with indexes"""
def create_table(connection):
    curs = connection.cursor()
    curs.execute("DROP TABLE Trio_Stat;")
    # curs.execute("DROP INDEX player1_attr")
    # curs.execute("DROP INDEX player2_attr")
    # curs.execute("DROP INDEX player3_attr")
    curs.execute("""CREATE TABLE Trio_Stat(
        id integer PRIMARY KEY,
        goals integer NOT NULL,
        shots integer NOT_NULL, """+attr_col_names_with_type("_1")+" , "+attr_col_names_with_type("_2")+", "+attr_col_names_with_type("_3")+");")
    
    #print("INDEX SQL:CREATE INDEX player1_attr on Trio_Stat ( "+PLAYER_1_ATTRS+" );")
    curs.execute("CREATE INDEX player1_attr on Trio_Stat ( "+PLAYER_1_ATTRS+" );")
    curs.execute("CREATE INDEX player2_attr on Trio_Stat ( "+PLAYER_2_ATTRS+" );")
    curs.execute("CREATE INDEX player3_attr on Trio_Stat ( "+PLAYER_3_ATTRS+" );")

def insert_trio_stat(curs, goals, shots, player1, player2, player3):
    curs.execute("""INSERT INTO Trio_Stat ( goals, shots, """+trio_stat_columns_str(['_1','_2','_3'])+
    " ) VALUES ( 0, 0,"+player_to_string(player1)+", "+player_to_string(player2)+", "+player_to_string(player3)+" );")

"""Return a tuple (player2, player3) containing player1 partnerts""" 
def partners(player1, curs):
    curs.execute("SELECT "+PLAYER_2_ATTRS+", " +PLAYER_3_ATTRS+"from Trio_Stat where "+player_atrr_cmp_str(player1,'_1')+";")
    partners = curs.fetchone()
    if partners is None:
        return None
    else:
        return (partners[:len(attr_columns)], partners[len(attr_columns)+1 : ])    

def player2(player1, curs):
    curs.execute("SELECT "+PLAYER_2_ATTRS+" from Trio_Stat where "+player_atrr_cmp_str(player1,'_1')+";")
    curs.fetchone()

def player3(player1, curs):
    curs.execute("SELECT "+PLAYER_3_ATTRS+" from Trio_Stat where "+player_atrr_cmp_str(player1,'_1')+";")
    curs.fetchone()

"""Returns a stats tuple (id, goals, shots) of player1 playing with player2 and 3
    None if trio stats not found"""
def trio_stats(player1, player2, player3, curs, tolerance=0):
    #print("QUERY: SELECT shots from Trio_Stat where "+player_atrr_cmp_str(player1, '_1')+ ' and '+player_atrr_cmp_str(player2, '_2')+' and '+player_atrr_cmp_str(player3, '_3')+";")
    curs.execute("SELECT id, goals, shots from Trio_Stat where "+player_atrr_cmp_str(player1, '_1',tolerance)+ ' and '+partners_query_condition(player2, player3, tolerance)+";")
    return curs.fetchone()

def _goals(player1, player2, player3, curs,tolerance=0):
    # sql = "SELECT max(goals) from Trio_Stat where "+player_atrr_cmp_str(player1, '_1',tolerance)+ ' and '+partners_query_condition(player2, player3,tolerance)+";"
    # print("SQL: ", sql)
    curs.execute("SELECT max(goals) from Trio_Stat where "+player_atrr_cmp_str(player1, '_1',tolerance)+ ' and '+partners_query_condition(player2, player3,tolerance)+";")
    return curs.fetchone()

def goals(player1, player2, player3, curs,tolerance=0):
    g23 = _goals(player1, player2, player3, curs, tolerance)
    g32 = _goals(player1, player3, player2, curs, tolerance)
    #_goals result is always a tuple with one element
    if g23[0] is None:
        return g32[0]
    elif g32[0] is None:
        return g23[0]
    else: #both not None
        return max(g23[0], g32[0])   

def shots(player1, player2, player3, curs):
    curs.execute("SELECT shots from Trio_Stat where "+player_atrr_cmp_str(player1, '_1')+ ' and '+partners_query_condition(player2, player3)+";")
    return curs.fetchone()

def id(player1, player2, player3, curs):
    curs.execute("SELECT id from Trio_Stat where "+player_atrr_cmp_str(player1, '_1')+ ' and '+partners_query_condition(player2, player3)+";")
    return curs.fetchone()

def increment_goals(increment, player1, player2, player3, curs):
    curs.execute("UPDATE Trio_Stat SET goals = goals + "+str(increment)+
    " where "+player_atrr_cmp_str(player1, '_1')+ ' and '+partners_query_condition(player2, player3)+";")

def increment_shots(increment, player1, player2, player3, curs):
    curs.execute("UPDATE Trio_Stat SET shots = shots + "+str(increment)+
    " where "+player_atrr_cmp_str(player1, '_1')+ ' and '+partners_query_condition(player2, player3)+";")

def increment_goals_and_shots(ginc,sinc, player1, player2, player3, curs):
    curs.execute("UPDATE Trio_Stat SET goals = goals + "+str(ginc)+ ", shots = shots + "+str(sinc)+
    " where "+player_atrr_cmp_str(player1, '_1')+ ' and '+partners_query_condition(player2, player3)+";")

def id_increment_goals(increment, id, curs):
    curs.execute("UPDATE Trio_Stat SET goals = goals + "+str(increment)+" where id = "+str(id)+";")

def id_increment_shots(increment, id, curs):
    curs.execute("UPDATE Trio_Stat SET shots = shots + "+str(increment)+" where id = "+str(id)+";")
    
def id_increment_goals_and_shots(ginc,sinc,id, curs):
    curs.execute("UPDATE Trio_Stat SET goals = goals + "+str(ginc)+ ", shots = shots + "+str(sinc)+
    " where id = "+str(id)+";")