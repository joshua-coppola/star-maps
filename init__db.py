import sqlite3
import csv
import os


def format_name(name: str) -> str:
    """
    Converts a string to have all major words capitalized

    #### Arguments:

    - name - string

    #### Returns:

    - name - formatted name
    """
    name_list = name.split('_')
    name = ''
    for word in name_list:
        if word[:3] == 'mcc':
            word = 'McC' + word[3:]
            name = '{}{} '.format(name, word)
            continue
        if len(word) > 2 or word == 'fe':
            name = '{}{} '.format(name, word.capitalize())
        else:
            name = '{}{} '.format(name, word)
    return name.strip()


connection = sqlite3.connect('databases.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

with open('../Ski-Trail-Ratings/mountain_list.csv', 'r') as fin:
    dr = csv.DictReader(fin)
    todb = [(i['mountain'], i['file_name'], i['direction'], i['state'], i['region'], i['difficulty'],
             30 - float(i['ease']), int(float(i['vert']) * 100 / (2.54 * 12)), i['trail_count'], i['lift_count']) for i in dr]
cur.executemany("INSERT INTO Mountains (name, osm_file_name, direction, state, region, difficulty, beginner_friendliness, vertical, trail_count, lift_count) VALUES (? , ?, ?, ?, ?, ?, ?, ?, ?, ?);", todb)

for filename in os.scandir(r'../Ski-Trail-Ratings/cached/trails'):
    with open(filename.path, 'r') as fin:
        dr = csv.DictReader(fin)
        mountainname = str(os.path.basename(filename.path))
        mountainname = mountainname.replace('.csv', '')
        mountainname = format_name(mountainname)
        mountainid = str(cur.execute(
            'SELECT mountainid FROM Mountains WHERE name = ?', (mountainname,)).fetchone())
        mountainid = ''.join(x for x in mountainid if x.isdigit())
        todb = [(i['name'], i['is_area'], (float(i['steepest_pitch']) + (float(i['difficulty_modifier']) * 7)), i['difficulty_modifier'],
                 i['steepest_pitch'], i['vert'], i['length'], i['id'], mountainid) for i in dr]
    cur.executemany("INSERT INTO Trails (name, is_area, difficulty, difficulty_modifier, steepest_pitch, vertical_drop, length, trailid, mountainid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", todb)

for filename in os.scandir(r'../Ski-Trail-Ratings/cached/lifts'):
    with open(filename.path, 'r') as fin:
        dr = csv.DictReader(fin)
        mountainname = str(os.path.basename(filename.path))
        mountainname = mountainname.replace('.csv', '')
        mountainname = format_name(mountainname)
        mountainid = str(cur.execute(
            'SELECT mountainid FROM Mountains WHERE name = ?', (mountainname,)).fetchone())
        mountainid = ''.join(x for x in mountainid if x.isdigit())
        todb = [(i['name'], i['id'], mountainid) for i in dr]
    cur.executemany(
        "INSERT INTO Lifts (name, liftid, mountainid) VALUES (?, ?, ?);", todb)

for filename in os.scandir(r'../Ski-Trail-Ratings/cached/trail_points'):
    with open(filename.path, 'r') as fin:
        dr = csv.DictReader(fin)
        todb = [(i['index'], i['trail_id'], i['for_display'], i['lat'],
                 i['lon'], i['elevation'], i['slope']) for i in dr]
    cur.executemany(
        "INSERT INTO TrailPoints (ind, trailid, for_display, latitude, longitude, elevation, slope) VALUES (?, ?, ?, ?, ?, ?, ?);", todb)


for filename in os.scandir(r'../Ski-Trail-Ratings/cached/lift_points'):
    with open(filename.path, 'r') as fin:
        dr = csv.DictReader(fin)
        todb = [(i['index'], i['lift_id'], i['lat'],
                 i['lon'], i['elevation']) for i in dr]
    cur.executemany(
        "INSERT INTO LiftPoints (ind, liftid, latitude, longitude, elevation) VALUES (?, ?, ?, ?, ?);", todb)

print("complete")
connection.commit()
connection.close()
