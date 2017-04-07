from bottle import route, run, template, static_file, error, request, response, view
import os
import signal
import string
import configparser
import json
from naomigame import *
from loadgame import *

PREFS_FILE = "settings.cfg"
prefs = configparser.ConfigParser()

loadingjob = loadjob(1, 1)
games = []

def build_games_list():
    games_directory = prefs['Games']['directory'] or 'games'

    print("Looking for NAOMI games...")

    if os.path.isdir(games_directory):
        for filename in os.listdir(games_directory):
            filename = games_directory + '/' + filename
            if(is_naomi_game(filename)):
                print(filename)
                game = NAOMIGame(filename)
                games.append(game)

        return games

    else:
        return None

@route('/')
def index():
    global games
    games = []
    games = build_games_list()
    region = prefs['Games']['region'].lower() or 'japan'
    
    if games != None:
        return template('index', games=games, region=region)
    else:
        return template('index')


@route('/load/<hashid:int>')
def load(hashid):
    global loadingjob
    if loadingjob.finished() == False:
        return 
    else:
        some_games = build_games_list()
        for game in some_games:
            if game.__hash__() == hashid:
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

    return template('config', network_ip=network_ip, network_subnet=network_subnet, games_directory=games_directory, games_region=games_region)

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

prefs_file = open(PREFS_FILE, 'r')
prefs.read_file(prefs_file)
prefs_file.close()

run(host='0.0.0.0', port=8000, debug=True)
