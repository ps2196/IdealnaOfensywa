import sqlite3
""" Find set of player attributes that has existing player for each attirbute value"""
path = "input/"  #Insert path here
database = path + 'database.sqlite'
conn = sqlite3.connect(database)
c = conn.cursor()

attribute_names = ['overall_rating', 'crossing', 'finishing', 'heading_accuracy', 'short_passing',
        'volleys', 'dribbling', 'curve', 'free_kick_accuracy', 'long_passing', 'ball_control', 'acceleration', 'sprint_speed','agility', 'reactions', 'balance',
        'shot_power', 'jumping', 'stamina','strength', 'long_shots', 'aggression', 'interceptions', 'positioning','vision', 'penalties', 'marking', 'standing_tackle', 'sliding_tackle']

complete_attrs = []
attributes_str = ""
for attr_name in attribute_names:
    c.execute("SELECT count(DISTINCT  "+attr_name+") as vals_count , min("+attr_name+") as min_val, max("+attr_name+") as max_val  from  Player_Attributes;")
    for row in c.fetchall():
        if row[0] ==(row[2] - row[1] + 1):
            complete_attrs.append(attr_name)
            attributes_str += attr_name+", "
        print(attr_name+"\t"+str(row[0])+" | "+str(row[1])+" | "+str(row[2]))

print("\n\nATTR WITH NO NULL VALUES: ")
c.execute("""SELECT * from Player_Attributes""")
attrs_count = len(c.fetchall())
non_null = []
for attr_name in attribute_names:
        c.execute(""" SELECT count(*) from Player_Attributes where """+attr_name+""" not NULL""")
        count = c.fetchone() 
        if  count == attrs_count:
                non_null.append(attr_name)
        print(attr_name,"\t", count, " of ", attrs_count)

