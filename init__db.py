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
    to_db = [(i['mountain'], i['file_name'], i['direction'], i['state'], i['region'], i['difficulty'],
             30 - float(i['ease']), int(float(i['vert']) * 100 / (2.54 * 12)), i['trail_count'], i['lift_count']) for i in dr]


cur.executemany("INSERT INTO Mountains (name, osm_file_name, direction, state, region, difficulty, beginner_friendliness, vertical, trail_count, lift_count) VALUES (? , ?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)

for filename in os.scandir(r'../Ski-Trail-Ratings/cached/trails'):
    with open(filename.path, 'r') as fin:
        dr = csv.DictReader(fin)
        mountain_name = str(os.path.basename(filename.path))
        mountain_name = mountain_name.replace('.csv', '')
        mountain_name = format_name(mountain_name)
        mountain_id = str(cur.execute(
            'SELECT mountain_id FROM Mountains WHERE name = ?', (mountain_name,)).fetchone())
        mountain_id = ''.join(x for x in mountain_id if x.isdigit())
        to_db = [(i['name'], i['is_area'], (float(i['steepest_pitch']) + (float(i['difficulty_modifier']) * 7)), i['difficulty_modifier'],
                 i['steepest_pitch'], i['vert'], i['length'], i['id'], mountain_id) for i in dr]
    for row in to_db:
        issue_area = cur.execute(
            "SELECT mountain_id, name, trail_id FROM Trails WHERE trail_id = ?", (row[7],))
    for row in issue_area:
        print(row)
    cur.executemany("INSERT INTO Trails (name, is_area, difficulty, difficulty_modifier, steepest_pitch, vertical_drop, length, trail_id, mountain_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)

for filename in os.scandir(r'../Ski-Trail-Ratings/cached/lifts'):
    with open(filename.path, 'r') as fin:
        dr = csv.DictReader(fin)
        mountain_name = str(os.path.basename(filename.path))
        mountain_name = mountain_name.replace('.csv', '')
        mountain_name = format_name(mountain_name)
        mountain_id = str(cur.execute(
            'SELECT mountain_id FROM Mountains WHERE name = ?', (mountain_name,)).fetchone())
        mountain_id = ''.join(x for x in mountain_id if x.isdigit())
        to_db = [(i['name'], i['id'], mountain_id) for i in dr]
    cur.executemany(
        "INSERT INTO Lifts (name, lift_id, mountain_id) VALUES (?, ?, ?);", to_db)

for filename in os.scandir(r'../Ski-Trail-Ratings/cached/trail_points'):
    with open(filename.path, 'r') as fin:
        dr = csv.DictReader(fin)
        to_db = [(i['index'], i['trail_id'], i['for_display'], i['lat'],
                 i['lon'], i['elevation'], i['slope']) for i in dr]
    cur.executemany(
        "INSERT INTO TrailPoints (ind, trail_id, for_display, latitude, longitude, elevation, slope) VALUES (?, ?, ?, ?, ?, ?, ?);", to_db)


for filename in os.scandir(r'../Ski-Trail-Ratings/cached/lift_points'):
    with open(filename.path, 'r') as fin:
        dr = csv.DictReader(fin)
        to_db = [(i['index'], i['lift_id'], i['lat'],
                 i['lon'], i['elevation']) for i in dr]
    cur.executemany(
        "INSERT INTO LiftPoints (ind, lift_id, latitude, longitude, elevation) VALUES (?, ?, ?, ?, ?);", to_db)

print("complete")
connection.commit()
connection.close()
