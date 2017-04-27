from bottle import route, run, template, static_file, error, request, response, view
import os
import signal
import string
import configparser
import json
import sqlite3
from naomigame import *
from loadgame import *

PREFS_FILE = "settings.cfg"
prefs = configparser.ConfigParser()
sql = None
loadingjob = loadjob(1, 1)
games = []
filters = []


#this function is pretty spaghetti but further abstraction really isn't necessary
def build_games_list():
    global sql
    games = []

    games_directory = prefs['Games']['directory'] or 'games'

    #get list of installed games
    installed_games = sql.execute("SELECT installed_games.id, games.id as game_id, filename, games.title as game_name, file_hash FROM installed_games JOIN games ON game_id=games.id ORDER BY game_name").fetchall()
    
    #check to make sure all the games we think are installed actually are. if not, purge them from the DB.
    print("Checking installed games")
    for igame in installed_games:
        filepath = games_directory + '/' + igame[2]

        if not os.path.isfile(filepath):
            print(igame[2] + " no longer installed, purging from DB")
            sql.execute("DELETE FROM installed_games WHERE id=" + str(igame[0]))
            continue # process next item

        if(is_naomi_game(filepath)):

            print("\t" + igame[2])

            # perform checksum verification of ROM file against stored value
            game = NAOMIGame(filepath)
            if igame[4] != game.checksum:
                print("Checksum error in " + filename + " expected " + installed_game[4] + " got " + game.checksum)
                game.status = "error"

            game.id = igame[1]
            game.name = igame[3]
            game.attributes = sql.execute("SELECT attributes.name as name, attributes_values.value as value FROM game_attributes JOIN attributes ON game_attributes.attribute_id=attributes.id JOIN attributes_values ON attributes_values_id=attributes_values.id WHERE game_id=" + str(igame[1])).fetchall()
            games.append(game)

    #don't commit any changes until we successfully scan installed games
    sql.commit()



    print("Looking for new NAOMI games")

    if os.path.isdir(games_directory):
        for filename in os.listdir(games_directory):
            filepath = games_directory + '/' + filename

            #Loop through the games we fetched from the DB.
            #If this file is installed, no further processing necessary. Continue to the next game.
            installed = False
            for igame in installed_games:
                if igame[2] == filename:
                    installed = True
                    break;

            if installed: continue

            # Verify t
            if(is_naomi_game(filepath)):
                #print(filename)
                game = NAOMIGame(filepath)

                identity = sql.execute("SELECT id, title FROM games WHERE header_title='" + game.name + "' LIMIT 1").fetchone()
                #print(identity)
                
                if identity: #game is valid
                    installed_game = sql.execute("SELECT * FROM installed_games WHERE game_id = " + str(identity[0])).fetchone()
                    
                    if not installed_game:
                        print ("\tInstalling "  + filename)
                        sql.execute("INSERT INTO installed_games(game_id, filename, file_hash) VALUES(" + str(identity[0]) + ",'" + filename + "','" + game.checksum + "')")
                        installed_game = sql.execute("SELECT * FROM installed_games WHERE game_id = " + str(identity[0])).fetchone()

                    #FIXME: KNOWN ISSUE: IF TWO IDENTICAL-HEADER GAMES EXIST, THE SECOND WILL NEVER BE INSTALLED.
                    
                    print(filename + " identified as " + identity[1])
                    game.id = identity[0]
                    game.name = identity[1]
                    game.attributes = sql.execute("SELECT attributes.name as name, attributes_values.value as value FROM game_attributes JOIN attributes ON game_attributes.attribute_id=attributes.id JOIN attributes_values ON attributes_values_id=attributes_values.id WHERE game_id=" + str(installed_game[1])).fetchall()
                    games.append(game)
                else:
                    print("\tUnable to identify " + filename)
                    game.id = 0
                    game.name = filename
                    game.attributes = []
                    games.append(game)

        sql.commit()

    games.sort(key = lambda games: games.name.lower())
    return games


@route('/')
def index():
    global games
    
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
                
        return template('index', games=temp, activefilters=filters)
    elif games != None:
        return template('index', games=games, activefilters=filters)
    else:
        return template('index')


@route('/updatedb', method='POST')
def updatedb():
    #TODO: Handle file upload and reopen sqlite DB. Then rescan games
    #STUB
    return

@route('/rescan')
def rescan():
    global games
    games = build_games_list()

@route('/cleargames')
def cleargames():
    global sql
    sql.execute("DELETE FROM installed_games")
    sql.execute("VACUUM")
    sql.commit()

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
    if 'images/' in filepath and not os.path.isfile('static/'+filepath):
        return static_file('images/0.jpg', 'static')

    return static_file(filepath, 'static')

@error(404)
def error404(error):
    return '<p>Error: 404</p>'

sql = sqlite3.connect('naomiweb.sqlite')

prefs_file = open(PREFS_FILE, 'r')
prefs.read_file(prefs_file)
prefs_file.close()

filters = prefs.items('Filters') or []

games = build_games_list()

run(host='0.0.0.0', port=8000, debug=True)
