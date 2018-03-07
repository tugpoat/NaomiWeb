from pybus_core import PyBus
from naomigame import *
from loadgame import *

#THINGS THAT SHOULD HAVE THEIR OWN THREADS:

#main thread - message bus, job dispatcher : Communicate with UI and decide recieve requests to create jobs. probably will also issue requests to jobs to die.
#database functionality : receive requests from other threads and publish results.
#each individual load job : load and keep-alive any active games. terminate on request from ui or main thread. provide feedback to ui.
#ui : interact with user : send and recieve UI-related messages. may need to open independent connection to database in order to perform ui-related tasks.
#logging : record events and communicate them with the UI. Dump to a file in the event of catastrophic failure
#system configuration tasks : make changes to system configuration and reboot or restart system services as necessary. run as superuser or specific user with access and provide feedback to ui.

#BLOCKING AND NON-BLOCKING JOBS
#for jobs that we want to make the user wait for, implement a way to dispatch jobs as such (maybe an argument to the creation request from the UI?)
#and wait for the message that it has completed while stalling the UI and displaying some kind of friendly "HOLD YOUR SHIT" message.

PREFS_FILE = "settings.cfg"
prefs = configparser.ConfigParser()

print('spawning messagebus')
mbus = PyBus()


database = naomidb("naomiweb.sqlite")

games = []




def build_games_list():
    games = []

    games_directory = prefs['Games']['directory'] or 'games'

    #get list of installed games
    installed_games = database.getInstalledGames()
    
    #check to make sure all the games we think are installed actually are. if not, purge them from the DB.
    print("Checking installed games")
    for igame in installed_games:
        filepath = games_directory + '/' + igame[2]

        if not os.path.isfile(filepath):
            print(igame[2] + " no longer installed, purging from DB")
            database.rmInstalledGameById(igame[0])
            continue # process next item

        if(is_naomi_game(filepath)):

            print("\t" + igame[2])

            # perform checksum verification of ROM file against stored value if we've enabled that in config
            game = NAOMIGame(filepath, prefs['Main']['skip_checksum'] )
            game.status = None
            if prefs['Main']['skip_checksum']:
                game.checksum = igame[4]
            
            if not prefs['Main']['skip_checksum'] and igame[4] != game.checksum:
                print("Checksum error in " + filename + " expected " + installed_game[4] + " got " + game.checksum)
                game.status = "error"

            game.id = igame[1]
            game.name = igame[3]
            game.attributes = database.getGameAttributes(igame[1])

            games.append(game)



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

            # Verify that the file is actually a naomi netboot title and process it accordingly
            if(is_naomi_game(filepath)):
                #print(filename)
                game = NAOMIGame(filepath)
                identity = database.getGameInformation(game.name)
                
                if identity: #game is valid
                    installed_game = database.getInstalledGameByGameId(identity[0])
                    
                    if not installed_game:
                        print ("\tInstalling "  + filename)
                        database.installGame(identity[0], filename, game.checksum)
                        installed_game = database.getInstalledGameByGameId(identity[0])
                    
                    print(filename + " identified as " + identity[1])
                    game.id = identity[0]
                    game.name = identity[1]
                    game.attributes = database.getGameAttributes(installed_game[1])
                    games.append(game)
                else:
                    print("\tUnable to identify " + filename)
                    game.id = 0
                    game.status = ''
                    game.name = filename
                    game.attributes = []
                    games.append(game)

    games.sort(key = lambda games: games.name.lower())
    return games
