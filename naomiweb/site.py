from bottle import route, run, template, static_file, error, request, response, view
import os
import signal
import string
import configparser
import json
import sqlite3
import hashlib
import time
from naomigame import *
from loadgame import *

PREFS_FILE = "settings.cfg"
prefs = configparser.ConfigParser()
sql = None
loadingjob = loadjob(1, 1)
games = []
game_list = []
filters = []


#this function is pretty spaghetti but further abstraction really isn't necessary
def build_games_list():
    global sql
    global games_list
    games_directory = prefs['Games']['directory'] or 'games'

    print("Checking installed games")
    #check to make sure all the games we think are installed actually are. if not, purge them from the DB.
    installed_games = sql.execute("SELECT id, filename, file_hash FROM installed_games").fetchall()
    for game in installed_games:
        if not os.path.isfile(game[1]):
            print(game[1] + " no longer installed, purging from DB")
            sql.execute("DELETE FROM installed_games WHERE id=" + str(game[0]))

    sql.commit()

    print("Looking for NAOMI games")

    if os.path.isdir(games_directory):
        for filename in os.listdir(games_directory):
            filename = games_directory + '/' + filename
            if(is_naomi_game(filename)):
                print(filename)
                game = NAOMIGame(filename)

                identity = sql.execute("SELECT * FROM games WHERE header_title='" + game.name['japan'] + "' LIMIT 1").fetchone()
                print(identity)
                
                if identity: #game is valid, check it and get its attributes
                    installed_game = sql.execute("SELECT * FROM installed_games WHERE game_id = " + str(identity[0])).fetchone()
                    print("valid game")

                    game.name = identity[2]

                    if installed_game:
                        #if game installed, verify integrity from stored checksum
                        print("game installed")
                        if game.checksum != installed_game[3]:
                            print("Checksum error in " + filename + " expected " + installed_game[3] + " got " + checksum)
                            game.status = "error"
                        
                        game.checksum = installed_game[3]
                    else:
                        print ("installing"  + filename)
                        sql.execute("INSERT INTO installed_games(game_id, filename, file_hash) VALUES(" + str(identity[0]) + ",'" + filename + "','" + game.checksum + "')")
                    
                    attributes = sql.execute("SELECT attributes.name as name, attributes_values.value as value FROM game_attributes JOIN attributes ON game_attributes.attribute_id=attributes.id JOIN attributes_values ON attributes_values_id=attributes_values.id WHERE game_id=" + str(identity[0])).fetchall()
                    game.attributes = attributes

                    games.append(game)

                    print(games[0].attributes)
        sql.commit()
        return games

    else:
        return None

@route('/')
def index():
    global games
    region = prefs['Games']['region'].lower() or 'japan'
    if games != None and len(filters) > 0:
        temp = []

        # Loop through filters for each game, and if an attribute matches the filter include it in the list. simple, effective.
        num_filters = len(filters)
        for g in games:
            num_matched = 0
            for f in filters:
                for a in g.attributes:
                    if f[0] == a[0] and f[1] == a[1]:
                        num_matched += 1

            if num_filters == num_matched:
                temp.append(g)
                
        return template('index', games=temp, region=region, filters=filters)
    elif games != None:
        return template('index', games=games, region=region, filters=filters)
    else:
        return template('index')

@route('/rescan')
def rescan():
    global games
    games = build_games_list()

@route('/filter/add/<name>/<value>')
def add_filter(name, value):
    filters.append((name,value))

@route('/filter/clear')
def clear_filters():
    filters.clear()

@route('/filter/get')
def get_filters():
    return json.dumps(filters)

@route('/load/<hashid>')
def load(hashid):
    global loadingjob
    if loadingjob.finished() == False:
        return 
    else:
        for game in games:
            if game.checksum == hashid:
                loadingjob = loadjob(game, prefs)
                loadingjob.start()

                return

    return "data: " + json.dumps({"status": loadingjob.status(), "message": "Unable to find " + str(hashid) + '!'}) + "\n\n"

@route('/status')
def status():
    global loadingjob
    response.content_type = "text/event-stream"
    response.cache_control = "no-cache"
    return "data: " + json.dumps({"status": loadingjob.status(), "message": loadingjob.message()}) + "\n\n"
    

@route('/config', method='GET')
def config():
    network_ip = prefs['Network']['ip'] or '192.168.0.10'
    network_subnet = prefs['Network']['subnet'] or '255.255.255.0'
    games_directory = prefs['Games']['directory'] or 'games'
    games_region = prefs['Games']['region'].lower() or 'japan'

    return template('config', network_ip=network_ip, network_subnet=network_subnet, games_directory=games_directory, games_region=games_region, filters=filters)

@route('/config', method='POST')
def do_config():
    network_ip = request.forms.get('network_ip')
    network_subnet = request.forms.get('network_subnet')
    games_directory = request.forms.get('games_directory')
    games_region = request.forms.get('selRegion')

    prefs['Network']['ip'] = network_ip
    prefs['Network']['subnet'] = network_subnet
    prefs['Games']['directory'] = games_directory
    prefs['Games']['region'] = games_region
    with open(PREFS_FILE, 'w') as prefs_file:
        prefs.write(prefs_file)

    return template('config', network_ip=network_ip, network_subnet=network_subnet, games_directory=games_directory, games_region=games_region, did_config=True)

@route('/favicon.ico')
def favicon():
    return static_file('favicon.ico', 'static')

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, 'static')

@error(404)
def error404(error):
    return '<p>Error: 404</p>'

sql = sqlite3.connect('naomiweb.sqlite')

prefs_file = open(PREFS_FILE, 'r')
prefs.read_file(prefs_file)
prefs_file.close()

filters = prefs.items('Filters') or []

build_games_list()

run(host='0.0.0.0', port=8000, debug=True)
