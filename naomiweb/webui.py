#this will be the new site.py with messagebus and thread support.
#turns out threading in python is super gross so I'm sorry about everything

from main import mbus, database
from bottle import Bottle
import threading

class WebUI(Bottle):
    def __init__(self, name):
        super(MyApp, self).__init__()
        self.name = name
        #set up routes
        self.route('/', callback=self.index)

    def index(self):
        return self.template('index')

    #TODO: other routes
