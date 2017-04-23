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

    def __get_name(self):
        'Get game names from NAOMI rom file.'
        try:
            fp = open(self.filepath, 'rb')
            fp.seek(0x30, os.SEEK_SET)

            self.name = fp.read(32).decode('utf-8').rstrip(' ').lstrip(' ')

            fp.close()
        except Exception:
            print("__get_names(): Error reading names from" + self.filename)

    def __init__(self, filepath):
        self.name = ''
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.__get_name()
        self.checksum = self.__checksum();
        try:
            self.size = os.stat(filepath).st_size
        except Exception:
            self.size = 0

    def __checksum(self):
        with open(self.filepath, 'rb') as fh:
            m = hashlib.md5()
            while True:
                data = fh.read(8192)
                if not data:
                    break
                m.update(data)
                
            return m.hexdigest()

    def __hash__(self):
        return hash((self.name, self.filepath, self.size)) & 0xffffffff


# Having functions like this in this module is a little gross. TODO: incorporate this functionality into the class.
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