import io
import os
import hashlib

class NAOMIGame(object):
    _name = None
    _filename = None
    _size = None
    _file_hash = None
    _attributes = None
    status = None

    def __get_names(self):
        'Get game names from NAOMI rom file.'
        try:
            fp = open(self.filename, 'rb')
            fp.seek(0x30, os.SEEK_SET)

            self.name['japan'] = fp.read(32).decode('utf-8').rstrip(' ')
            self.name['usa'] = fp.read(32).decode('utf-8').rstrip(' ')
            self.name['euro'] = fp.read(32).decode('utf-8').rstrip(' ')
            self.name['asia'] = fp.read(32).decode('utf-8').rstrip(' ')
            self.name['australia'] = fp.read(32).decode('utf-8').rstrip(' ')

            fp.close()
        except Exception:
            print("__get_names(): Error reading names from" + self.filename)

    def __init__(self, filename):
        self.name = {'japan': '',
                'usa': '',
                'euro': '',
                'asia': '',
                'australia': ''}
        self.filename = filename
        self.__get_names()
        self.checksum = self.__checksum();
        try:
            self.size = os.stat(filename).st_size
        except Exception:
            self.size = 0

    def __checksum(self):
        with open(self.filename, 'rb') as fh:
            m = hashlib.md5()
            while True:
                data = fh.read(8192)
                if not data:
                    break
                m.update(data)
                
            return m.hexdigest()

    def __hash__(self):
        return hash((self.name['japan'], self.filename, self.size)) & 0xffffffff

def is_naomi_game(filename):
    'Determine (loosely) if a file is a valid NAOMI netboot game'
    try:
        fp = open(filename, 'rb')
        header_magic = fp.read(5).decode('utf-8')
        fp.close()
        return header_magic == 'NAOMI'

    except Exception:
        print("is_naomi_game(): Could not open " + filename)
        return False

def get_game_name(filename):
    'Read game name from NAOMI rom file.'
    try:
        fp = open(filename, 'rb')
        fp.seek(0x30, os.SEEK_SET)
        filename = fp.read(32).decode('utf-8').rstrip(' ').lstrip(' ')
        fp.close()
        return filename

    except Exception:
        print("get_game_name(): Error reading game name.")
        return ''