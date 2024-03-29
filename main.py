from re import I
from flask import Flask, render_template, json, redirect, url_for, request, flash, session, request
from flask_wtf import FlaskForm
from datetime import datetime
import sqlite3
from csv import DictReader
import json
import os

app = Flask(__name__, template_folder="templates",
            static_url_path='', static_folder="static")
app.config['SECRET_KEY'] = "placeholder"


class navlink:
    def __init__(self, title, page, to):
        self.title = title
        self.page = page
        self.to = to


navlinks = []
navlinks.append(navlink("About", "about", "/about"))
navlinks.append(navlink("Search", "search", "/search"))
navlinks.append(navlink("Rankings", "rankings",
                "/rankings?sort=difficulty&order=desc&region=usa"))

# Load the state abbreviation data
with open('states.csv', 'r') as fd:
    states_csv = DictReader(fd)
    states = {}
    for state in states_csv:
        states[state['Abbreviation']] = state['State']


def state_code_to_state(state_code):
    if state_code in states:
        return states[state_code]
    else:
        return state_code


class mountainToMapPage:
    def __init__(self, unique_name, name, state, statistics, trails, lifts):
        self.unique_name = unique_name
        self.name = name
        self.state = state_code_to_state(state)
        self.statistics = statistics
        self.trails = trails
        self.lifts = lifts


def getdbconnection():
    conn = sqlite3.connect('databases.db')
    conn.row_factory = sqlite3.Row
    return conn


def removesuffix(string, suffix):
    if suffix and string.endswith(suffix):
        return string[0:-len(suffix)]
    else:
        return string[:]


@app.route("/")
def index():
    return render_template("index.jinja", nav_links=navlinks, active_page="index")


@app.route("/about")
def about():
    return render_template("about.jinja", nav_links=navlinks, active_page="about")


@app.route("/search")
def search():
    # parsing query string for database search
    searchstring = ""
    q = request.args.get('q')
    if q and q != "%%":
        q = "%" + q + "%"
        searchstring += "q=" + q.replace("%", "") + "&"
    else:
        q = "%%"
    page = request.args.get('page')
    if not page:
        page = 1
    limit = request.args.get('limit')
    if not limit:
        limit = 20
    else:
        searchstring += "limit=" + str(limit) + "&"
    diffmin = request.args.get('diffmin')
    if not diffmin:
        diffmin = 0
    else:
        searchstring += "diffmin=" + str(diffmin) + "&"
    diffmax = request.args.get('diffmax')
    if not diffmax:
        diffmax = 100
    else:
        searchstring += "diffmax=" + str(diffmax) + "&"
    location = request.args.get('location')
    if not location or location == "%%":
        location = "%%"
    else:
        searchstring += "location=" + location + "&"
    trailsmin = request.args.get('trailsmin')
    if not trailsmin:
        trailsmin = 0
    else:
        searchstring += "trailsmin=" + str(trailsmin) + "&"
    trailsmax = request.args.get('trailsmax')
    if not trailsmax:
        trailsmax = 1000
    else:
        searchstring += "trailsmax=" + str(trailsmax) + "&"
    sort = request.args.get('sort')
    if not sort:
        sort = 'name'
    else:
        searchstring += "sort=" + sort + "&"
    order = request.args.get('order')
    if not order:
        order = 'asc'
    else:
        searchstring += "order=" + order + "&"

    queryParams = removesuffix(searchstring, '&')
    page = int(page)
    limit = int(limit)
    bottomlimit = limit*(page-1)

    conn = getdbconnection()
    mountains = conn.execute(f'SELECT * FROM Mountains WHERE name LIKE ? AND state LIKE ? AND trail_count >= ? AND trail_count <= ? AND difficulty >= ? AND difficulty <= ? ORDER BY {sort} {order} LIMIT ? OFFSET ?',
                             (q, location, trailsmin, trailsmax, diffmin, diffmax, limit, bottomlimit)).fetchall()
    elements = len(conn.execute('SELECT * FROM Mountains WHERE name LIKE ? AND state LIKE ? AND trail_count >= ? AND trail_count <= ? AND difficulty >= ? AND difficulty <= ?',
                   (q, location, trailsmin, trailsmax, diffmin, diffmax)).fetchall())

    mountains_data = []
    for mountain in mountains:
        name = mountain['name']
        mountains_data.append({
            'name': name,
            'beginner_friendliness': mountain['beginner_friendliness'],
            'difficulty': mountain['difficulty'],
            'state': state_code_to_state(mountain['state']),
            'trail_count': mountain['trail_count'],
            'vertical': mountain['vertical'],
            'map_link': url_for('map', mountain_id=mountain['mountain_id']),
            'thumbnail': f'thumbnails/{name}.svg'})

    conn.close()

    pages = {}
    if elements > limit and (limit * page) < elements:
        urlBase = "/search?page=" + str(page + 1) + "&"
        urlBase += queryParams
        urlQuery = removesuffix(urlBase, '&')
        pages["next"] = urlQuery
    if bottomlimit != 0:
        urlBase = "/search?page=" + str(page - 1) + "&"
        urlBase += queryParams
        urlQuery = removesuffix(urlBase, '&')
        pages["prev"] = urlQuery

    return render_template("mountains.jinja", nav_links=navlinks, active_page="search", mountains=mountains_data, pages=pages)


@ app.route("/rankings")
def rankings():
    sort = request.args.get('sort')
    if not sort:
        sort = "difficulty"
    order = request.args.get('order')
    if not order:
        order = "desc"
    region = request.args.get('region')
    if not region:
        region = "usa"
    # converts query string info into SQL
    conn = getdbconnection()
    mountainsFormatted = []
    if sort == "beginner":
        sort_by = "beginner_friendliness"
    else:
        sort_by = "difficulty"
    if region == "usa":
        mountains = conn.execute(
            f'SELECT * FROM Mountains ORDER BY {sort_by} {order}').fetchall()
    else:
        mountains = conn.execute(
            f'SELECT * FROM Mountains WHERE region = ? ORDER BY {sort_by} {order}', (region,)).fetchall()

    for mountain in mountains:
        mountainentry = {
            "name": mountain['name'],
            "beginner_friendliness": mountain['beginner_friendliness'],
            "difficulty": mountain['difficulty'],
            "state": mountain['state'],
            "map_link": url_for('map', mountain_id=mountain['mountain_id'])
        }
        mountainsFormatted.append(mountainentry)

    conn.close()
    return render_template("rankings.jinja", nav_links=navlinks, active_page="rankings", mountains=mountainsFormatted, sort=sort, order=order, region=region)


@ app.route("/map/<int:mountain_id>")
def map(mountain_id):
    conn = getdbconnection()

    mountain_row = conn.execute(
        'SELECT name, state, trail_count, lift_count, vertical FROM Mountains WHERE mountain_id = ?', (mountain_id,)).fetchone()
    if not mountain_row:
        return "404"

    statistics = {
        "Trail Count": mountain_row['trail_count'],
        "Lift Count": mountain_row['lift_count'],
        "Vertical": str(mountain_row['vertical']) + "'"
    }

    trails = conn.execute(
        'SELECT name, difficulty, steepest_pitch FROM Trails WHERE mountain_id = ? ORDER BY difficulty DESC', (mountain_id,)).fetchall()
    lifts = conn.execute(
        'SELECT name FROM Lifts WHERE mountain_id = ? ORDER BY name ASC', (mountain_id,)).fetchall()
    conn.close()

    mountain = mountainToMapPage(
        mountain_id, mountain_row['name'], mountain_row['state'], statistics, trails, lifts)

    return render_template("map.jinja", nav_links=navlinks, active_page="map", mountain=mountain)


@ app.route("/data/<int:mountain_id>/objects", methods=['GET'])
def mountaindata(mountain_id):
    conn = getdbconnection()
    trailrows = conn.execute(
        'SELECT * FROM Trails WHERE mountain_id = ?', (mountain_id,)).fetchall()
    liftrows = conn.execute(
        'SELECT lift_id, name FROM Lifts WHERE mountain_id = ?', (mountain_id,)).fetchall()
    conn.close()

    if not trailrows:
        return "404"

    jsonContents = {}
    trails = []
    lifts = []

    for trail in trailrows:
        trailentry = {
            "id": trail['trail_id'],
            "name": trail['name'],
            "difficulty": trail['difficulty'],
            "length": trail['length'],
            "vertical_drop": trail['vertical_drop'],
            "steepest_pitch": trail['steepest_pitch']
        }
        trails.append(trailentry)

    for lift in liftrows:
        liftentry = {
            "id": lift['lift_id'],
            "name": lift['name'],
        }
        lifts.append(liftentry)

    jsonContents['trails'] = trails
    jsonContents['lifts'] = lifts
    jsonstring = json.dumps(jsonContents)
    return jsonstring


@ app.route("/data/<int:mountain_id>/map.svg", methods=['GET'])
def svgmaps(mountain_id):
    conn = getdbconnection()
    mountainname = conn.execute(
        'SELECT name FROM Mountains WHERE mountain_id = ?', (mountain_id,)).fetchone()
    conn.close()

    if not mountainname:
        return "404"

    svgfilename = str(mountainname['name']) + ".svg"
    for filename in os.scandir('../Ski-Trail-Ratings/figures/maps'):
        strfilename = str(os.path.basename(filename.path))
        if strfilename == svgfilename:
            break
    with open('../Ski-Trail-Ratings/figures/maps/' + str(strfilename), 'r') as fileReturn:
        return fileReturn.read(), 200, {'Content-Type': 'image/svg+xml'}


@ app.route("/data/<int:mountain_id>/paths", methods=['GET'])
def pathdata(mountain_id):
    conn = getdbconnection()
    trails = conn.execute(
        'SELECT * FROM Trails WHERE mountain_id = ?', (mountain_id,)).fetchall()
    lifts = conn.execute(
        'SELECT * FROM Lifts WHERE mountain_id = ?', (mountain_id,)).fetchall()
    if not trails:
        conn.close()
        return "404"
    alltrails = []
    for trail in trails:
        trail_id = trail['trail_id']
        tpcontents = conn.execute(
            "SELECT latitude, longitude, elevation FROM TrailPoints WHERE trail_id = ?", (trail_id,))
        trailstring = ""
        for tp in tpcontents:
            trailstring += str(round(tp['latitude'], 5)) + "," + str(
                round(tp['longitude'], 5)) + "," + str(round(tp['elevation'], 1)) + "|"
        finaltrailstring = removesuffix(trailstring, "|")
        trailInput = {
            "id": trail_id,
            "points": finaltrailstring
        }
        alltrails.append(trailInput)

    allifts = []
    for lift in lifts:
        lift_id = lift['lift_id']
        lpcontents = conn.execute(
            "SELECT latitude, longitude, elevation FROM LiftPoints WHERE lift_id = ?", (lift_id,))
        liftstring = ""
        for lp in lpcontents:
            liftstring += str(round(lp['latitude'], 5)) + "," + str(
                round(lp['longitude'], 5)) + "," + str(round(lp['elevation'], 1)) + "|"
        finalliftstring = removesuffix(liftstring, "|")
        liftInput = {
            "id": lift_id,
            "points": finalliftstring
        }
        allifts.append(liftInput)

    finalJSON = {
        "trails": alltrails,
        "lifts": allifts
    }

    conn.close()
    jsonstring = json.dumps(finalJSON)
    return jsonstring


if __name__ == "__main__":
    app.run()
