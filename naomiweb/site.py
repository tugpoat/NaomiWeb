from bottle import route, run, template, static_file, error, request, response, view
from array import *
import os
import signal
import string
import configparser
import json
from naomidb import naomidb
from naomigame import *
from loadgame import *
from main import mbus, database

loadingjob = loadjob(1, 1)
filters = []

@route('/')
def index():

    #Get filter information from DB and format it all nice for the template
    filter_groups = database.getAttributes()
    filter_values = []

    for g in filter_groups:
        values = database.getValuesForAttribute(g[0])
        temp = []
        for v in values:
            temp.append(v)

        filter_values.append([g[0], temp])

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

            if num_matched == len(filters):
                temp.append(g)
                
        return template('index', games=temp, filter_groups=filter_groups, filter_values=filter_values, activefilters=filters)
    elif games != None:
        return template('index', games=games, filter_groups=filter_groups, filter_values=filter_values, activefilters=filters)
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
    database.purgeInstalledGames()

@route('/filter/add/<name>/<value>')
def add_filter(name, value):
    filters.append((name,value))

@route('/filter/rm/<name>/<value>')
def rm_filter(name, value):
    filters.remove((name, value))

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
    #ugh why is html so poopy for integrating with
    if prefs['Main']['skip_checksum'] == 'True':
        skip_checksum = 'checked'
    else:
        skip_checksum =  ''

    network_ip = prefs['Network']['ip'] or '192.168.0.10'
    network_subnet = prefs['Network']['subnet'] or '255.255.255.0'
    games_directory = prefs['Games']['directory'] or 'games'

    #render
    return template('config', skip_checksum=skip_checksum, network_ip=network_ip, network_subnet=network_subnet, games_directory=games_directory)

@route('/config', method='POST')
def do_config():
    skip_checksum = request.forms.get('skip_checksum')
    network_ip = request.forms.get('network_ip')
    network_subnet = request.forms.get('network_subnet')
    games_directory = request.forms.get('games_directory')

    if skip_checksum == 'on':
        skip_checksum = 'True'
    else:
        skip_checksum = 'False'

    prefs['Main']['skip_checksum'] = skip_checksum
    prefs['Network']['ip'] = network_ip
    prefs['Network']['subnet'] = network_subnet
    prefs['Games']['directory'] = games_directory

    with open(PREFS_FILE, 'w') as prefs_file:
        prefs.write(prefs_file)

    #rework this asshat for html
    if skip_checksum == 'True':
        skip_checksum = 'checked'
    else:
        skip_checksum = ''

    return template('config', network_ip=network_ip, network_subnet=network_subnet, games_directory=games_directory, skip_checksum=skip_checksum, did_config=True)

@route('/edit/<hashid>', method='GET')
def edit(hashid):
    g = None
    gamelist = database.getGameList()

    g = [game for game in games if game.checksum == hashid][0]

    return template('edit', filename=g.filename, game_title=g.name, hashid=hashid, games_list=gamelist)

@route('/edit/<hashid>', method='POST')
def do_edit(hashid):
    global games
    new_game_id = request.forms.get('games')
    filename = request.forms.get('filename')
    database.editGame(new_game_id, filename, hashid)
    # Just rebuild the list for now
    # FIXME: replace the list entry with the updated one instead
    games = build_games_list()

    # FIXME: Maybe kick them back to the index instead of doing all this?
    g = None
    gamelist = database.getGameList()

    g = [game for game in games if game.checksum == hashid][0]

    return template('edit', filename=g.filename, game_title=g.name, hashid=hashid, games_list=gamelist, did_edit=True)

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

prefs_file = open(PREFS_FILE, 'r')
prefs.read_file(prefs_file)
prefs_file.close()

filters = prefs.items('Filters') or []

games = build_games_list()

run(host='0.0.0.0', port=8000, debug=True)
