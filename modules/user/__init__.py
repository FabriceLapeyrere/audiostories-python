from db import DB
from ws import maj, get_verrou
import hashlib, json
class User(object):
	def __init__(self):
		db = DB()			# the database connection
		self.connexion=db.connexion
	def build_users(self,entries):
		res=[]
		for e in entries:
			e['verrou']=get_verrou('user/%s' % (e['id']))
			res.append(e)
		return res
	def get_users(self,iduser):
		return self.connexion.runQuery("SELECT id, login, name, role FROM users WHERE active=1").addCallback(self.build_users)
	def build_groups(self,entries):
		res=[]
		for e in entries:
			e['verrou']=get_verrou('group/%s' % (e['id']))
			try:
				e['users']=json.loads(e['users'])
			except:
				e['users']=[]
			res.append(e)
		return res
	def get_groups(self,iduser):
		return self.connexion.runQuery("SELECT t1.id, t1.nom, '[' || Group_Concat(DISTINCT t3.id ) ||']' as users FROM groups as t1 left outer join user_group as t2 on t1.id=t2.id_group left outer join users as t3 on t3.id=t2.id_user AND t3.active=1 group by t1.id").addCallback(self.build_groups)
	def build_group(self,entries):
		e=entries[0]
		e['verrou']=get_verrou('group/%s' % (e['id']))
		try:
			e['users']=json.loads(e['users'])
		except:
			e['users']=[]
		return e
	def get_group(self,groupid,iduser):
		return self.connexion.runQuery("SELECT t1.id, t1.nom, '[' || Group_Concat(DISTINCT t3.id ) ||']' as users FROM groups as t1 left outer join user_group as t2 on t1.id=t2.id_group left outer join users as t3 on t3.id=t2.id_user AND t3.active=1 WHERE t1.id=? group by t1.id",(groupid,)).addCallback(self.build_group)
	def build_users_all(self,entries):
		res={}
		for e in entries:
			res[e['id']]=e
		return res
	def get_users_all(self,iduser):
		return self.connexion.runQuery("SELECT id, login, name, role FROM users").addCallback(self.build_users_all)
	def get_user(self, userid, iduser):
		return self.connexion.runQuery("SELECT id, login, name, role FROM users WHERE active=1 AND id=?",(userid,)).addCallback(lambda e: e[0])
	def del_user(self,userid, iduser):
		if userid!=1 and iduser==1:
			return self.connexion.runQuery('UPDATE users set active=0 WHERE id=?',(userid,)).addCallback(lambda x: maj(["user/%s" % userid],userid,iduser))
		return False
	def do_add_user(self,txn,login,name,password,iduser):
		password=hashlib.md5(password).hexdigest()
		prefs={'panier':{}}
		txn.execute('INSERT INTO users (login, name, password, prefs, role, active) VALUES (?,?,?,?,?,?)',(login,name,password,json.dumps(prefs),1,1))
		return txn.lastrowid
	def add_user(self,login,name,password,iduser):
		if iduser==1:
			return self.connexion.runInteraction(self.do_add_user, login, name, password, iduser).addCallback(lambda userid: maj(["user/%s" % userid],userid,iduser))
		return False	
	def mod_user(self,userid,login,name,password,role,iduser):
		if iduser==1:
			if password=='':
				return self.connexion.runQuery('UPDATE users set name=?, role=? WHERE id=?',(name,role,userid)).addCallback(lambda x: maj(["user/%s" % userid],userid,iduser))
			else:
				password=hashlib.md5(password).hexdigest()
				return self.connexion.runQuery('UPDATE users set name=?, password=?, role=? WHERE id=?',(name,password,role,userid)).addCallback(lambda x: maj(["user/%s" % userid],userid,iduser))
		return False
	def mod_moi(self,userid,login,name,password,iduser):
		if iduser==userid:
			if password=='':
				return self.connexion.runQuery('UPDATE users set name=? WHERE id=?',(name,userid)).addCallback(lambda x: maj(["user/%s" % userid],userid,iduser))
			else:
				password=hashlib.md5(password).hexdigest()
				return self.connexion.runQuery('UPDATE users set name=?, password=? WHERE id=?',(name,password,userid)).addCallback(lambda x: maj(["user/%s" % userid],userid,iduser))
		return False
	def del_group(self,groupid, iduser):
		if iduser==1:
			return self.connexion.runQuery("DELETE FROM groups WHERE id=?",(groupid,)).addCallback(lambda x: maj(["group/%s" % groupid],groupid,iduser))
		return False
	def do_add_group(self,txn,nom,iduser):
		txn.execute('INSERT INTO groups (nom) VALUES (?)',(nom,))
		return txn.lastrowid
	def add_group(self,nom,iduser):
		if iduser==1:
			return self.connexion.runInteraction(self.do_add_group, nom, iduser).addCallback(lambda groupid: maj(["group/%s" % groupid],groupid,iduser))
	def mod_group(self,groupid,nom,iduser):
		if iduser==1:
			return self.connexion.runQuery('UPDATE groups set nom=? WHERE id=?',(nom,groupid)).addCallback(lambda x: maj(["group/%s" % groupid],groupid,iduser))
		return False
	def add_user_group(self,userid,groupid,iduser):
		if iduser==1:
			return self.connexion.runQuery('INSERT OR REPLACE INTO user_group (id_user,id_group) VALUES (?,?)',(userid,groupid)).addCallback(lambda x: maj(["*"],groupid,iduser))
	def del_user_group(self,userid,groupid,iduser):
		if iduser==1:
			return self.connexion.runQuery('DELETE FROM user_group WHERE id_user=? AND id_group=?',(userid,groupid)).addCallback(lambda x: maj(["*"],groupid,iduser))
	def add_acl(self,type_ressource,id_ressource,type_acces,id_acces,level,iduser):
		return self.connexion.runQuery("INSERT OR REPLACE INTO acl (type_ressource, id_ressource, type_acces, id_acces, level) SELECT ?,?,?,?,? WHERE ?=1 OR (? in (SELECT createdby FROM {} WHERE id=?))".format(type_ressource),(type_ressource,id_ressource,type_acces,id_acces,level,iduser,iduser,id_ressource)).addCallback(lambda x: maj(["*"],iduser,iduser));
	def is_allowed(self,type_ressource,id_ressource,level,iduser):
		return self.connexion.runQuery("SELECT 1 from {} WHERE id=? AND ( ?=1 OR createdby=? OR id IN (SELECT id_ressource from acl where type_ressource=? AND type_acces='group' AND id_acces IN (select id_group from user_group where id_user=?)))".format(type_ressource),(id_ressource,iduser,iduser,type_ressource,iduser)).addCallback(lambda x: len(x)==1)
	def del_acl(self,type_ressource,id_ressource,type_acces,id_acces,level,iduser):
		return self.connexion.runQuery("DELETE FROM acl WHERE type_ressource=? AND id_ressource=? AND type_acces=? AND id_acces=? AND level=? AND (?=1 OR (? in (SELECT createdby FROM {} WHERE id=?)))".format(type_ressource),(type_ressource,id_ressource,type_acces,id_acces,level,iduser,iduser,id_ressource)).addCallback(lambda x: maj(["*"],iduser,iduser));

