import sqlite3

class naomidb:
	_sqlite = None
	_dbfile = None

	def __init__(self, dbfile):
		self._dbfile = dbfile
		try:
			self._sqlite = sqlite3.connect(self._dbfile)
		except:
			print("failed to connect to sqlite db")
			return

	def getInstalledGames(self):
		return self._sqlite.execute("SELECT installed_games.id, games.id as game_id, filename, games.title as game_name, file_hash FROM installed_games JOIN games ON game_id=games.id ORDER BY game_name").fetchall()

	def getInstalledGame(self, game_id):
		return self._sqlite.execute("SELECT * FROM installed_games WHERE game_id = " + str(game_id) + " LIMIT 1").fetchone()

	def getGameAttributes(self, game_id):
		return self._sqlite.execute("SELECT attributes.name as name, attributes_values.value as value FROM game_attributes JOIN attributes ON game_attributes.attribute_id=attributes.id JOIN attributes_values ON attributes_values_id=attributes_values.id WHERE game_id=" + str(game_id)).fetchall()

	def installGame(self, game_id, filename, file_hash):
		self._sqlite.execute("INSERT INTO installed_games(game_id, filename, file_hash) VALUES(" + str(game_id) + ",'" + filename + "','" + file_hash + "')")
		self._sqlite.commit()

	def rmInstalledGameById(self, installed_game_id):
		self._sqlite.execute("DELETE FROM installed_games WHERE id=" + str(installed_game_id))
		self._sqlite.commit()

	def purgeInstalledGames(self):
		self._sqlite.execute("DELETE FROM installed_games")
		self._sqlite.execute("VACUUM")
		self._sqlite.commit()

	def getGameInformation(self, header_title):
		self._sqlite.execute("SELECT id, title FROM games WHERE header_title='" + str(header_title) + "' LIMIT 1").fetchone()

	def getAttributes(self):
		return self._sqlite.execute("SELECT * FROM attributes").fetchall()

	def getValuesForAttribute(self, attribute_id):
		return self._sqlite.execute("SELECT id, value from attributes_values WHERE attribute_id=" + str(attribute_id)).fetchall()

