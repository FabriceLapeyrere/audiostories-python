import os
from twisted.enterprise import adbapi
import hashlib
import sqlite3

class DB(object):
	def __init__(self):
		dbname='data/db/db.sqlite'
		dbdir='data/db/'
		if not os.path.isdir(dbdir):
			os.makedirs(dbdir)
		if not os.path.isfile(dbname):
			conn = sqlite3.connect(dbname)
			curs = conn.cursor()
			curs.execute("CREATE TABLE stories (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, desc TEXT, pitch TEXT, couleur TEXT, sons TEXT, photos TEXT, statut INTEGER, date INTEGER, creationdate INTEGER, createdby INTEGER, modificationdate INTEGER, modifiedby INTEGER)")
			curs.execute("CREATE TABLE tag_story (id TEXT PRIMARY KEY, id_tag INTEGER, id_story INTEGER, date INTEGER)")
			curs.execute("CREATE TABLE trash (id INTEGER PRIMARY KEY AUTOINCREMENT, id_item INTEGER, type TEXT, json TEXT, date INTEGER, by INTEGER)")
			curs.execute("CREATE TABLE pages (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, html TEXT, statut INTEGER, creationdate INTEGER, createdby INTEGER, modificationdate INTEGER, modifiedby INTEGER)")
			curs.execute("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, login TEXT, name TEXT, password TEXT, prefs TEXT, role INTEGER DEFAULT 1, active INTEGER DEFAULT 1)")
			curs.execute("CREATE TABLE groups (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT)")
			curs.execute("CREATE TABLE acl (id_ressource INTEGER, type_ressource TEXT, id_acces INTEGER, type_acces TEXT, level INTEGER)")
			curs.execute("CREATE TABLE user_group (id_user INTEGER, id_group INTEGER)")
			curs.execute("CREATE UNIQUE INDEX acl_idx on acl(id_ressource, type_ressource, id_acces, type_acces)")
			curs.execute("CREATE UNIQUE INDEX user_group_idx on user_group(id_user, id_group)")
			adminpass = hashlib.md5("adminadmin").hexdigest()
			curs.execute("INSERT INTO users (login, name, password, prefs, role, active) VALUES (?,?,?,?,?,?)", ("admin", "Admin", adminpass, "{}", 2, 1))
			conn.commit()
			curs.close()
		self.connexion=adbapi.ConnectionPool("sqlite3", dbname, check_same_thread=False,cp_openfun=self.set_dict_factory)
	def dict_factory(self, cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d

	def set_dict_factory(self, conn):
		conn.row_factory = self.dict_factory

