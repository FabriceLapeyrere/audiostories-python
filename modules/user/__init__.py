import db, ws, sys, hashlib, json

this = sys.modules[__name__]
def build_users(entries):
	res=[]
	for e in entries:
		e['verrou']=ws.get_verrou('user/%s' % (e['id']))
		res.append(e)
	return res
def get_users(iduser):
	return db.connexion.runQuery("SELECT id, login, name, role FROM users WHERE active=1").addCallback(this.build_users)
def build_groups(entries):
	res=[]
	for e in entries:
		e['verrou']=ws.get_verrou('group/%s' % (e['id']))
		try:
			e['users']=json.loads(e['users'])
		except:
			e['users']=[]
		res.append(e)
	return res
def get_groups(iduser):
	return db.connexion.runQuery("SELECT t1.id, t1.nom, '[' || Group_Concat(DISTINCT t3.id ) ||']' as users FROM groups as t1 left outer join user_group as t2 on t1.id=t2.id_group left outer join users as t3 on t3.id=t2.id_user AND t3.active=1 group by t1.id").addCallback(this.build_groups)
def build_group(entries):
	e=entries[0]
	e['verrou']=ws.get_verrou('group/%s' % (e['id']))
	try:
		e['users']=json.loads(e['users'])
	except:
		e['users']=[]
	return e
def get_group(groupid,iduser):
	return db.connexion.runQuery("SELECT t1.id, t1.nom, '[' || Group_Concat(DISTINCT t3.id ) ||']' as users FROM groups as t1 left outer join user_group as t2 on t1.id=t2.id_group left outer join users as t3 on t3.id=t2.id_user AND t3.active=1 WHERE t1.id=? group by t1.id",(groupid,)).addCallback(this.build_group)
def build_users_all(entries):
	res={}
	for e in entries:
		res[e['id']]=e
	return res
def get_users_all(iduser):
	return db.connexion.runQuery("SELECT id, login, name, role FROM users").addCallback(this.build_users_all)
def get_user( userid, iduser):
	return db.connexion.runQuery("SELECT id, login, name, role FROM users WHERE active=1 AND id=?",(userid,)).addCallback(lambda e: e[0])
def del_user(userid, iduser):
	if userid!=1 and iduser==1:
		return db.connexion.runQuery('UPDATE users set active=0 WHERE id=?',(userid,)).addCallback(lambda x: ws.maj(["user/%s" % userid],userid,iduser))
	return False
def do_add_user(txn,login,name,password,iduser):
	password=hashlib.md5(password).hexdigest()
	prefs={'panier':{}}
	txn.execute('INSERT INTO users (login, name, password, prefs, role, active) VALUES (?,?,?,?,?,?)',(login,name,password,json.dumps(prefs),1,1))
	return txn.lastrowid
def add_user(login,name,password,iduser):
	if iduser==1:
		return db.connexion.runInteraction(this.do_add_user, login, name, password, iduser).addCallback(lambda userid: ws.maj(["user/%s" % userid],userid,iduser))
	return False	
def mod_user(userid,login,name,password,role,iduser):
	if iduser==1:
		if password=='':
			return db.connexion.runQuery('UPDATE users set name=?, role=? WHERE id=?',(name,role,userid)).addCallback(lambda x: ws.maj(["user/%s" % userid],userid,iduser))
		else:
			password=hashlib.md5(password).hexdigest()
			return db.connexion.runQuery('UPDATE users set name=?, password=?, role=? WHERE id=?',(name,password,role,userid)).addCallback(lambda x: ws.maj(["user/%s" % userid],userid,iduser))
	return False
def mod_moi(userid,login,name,password,iduser):
	if iduser==userid:
		if password=='':
			return db.connexion.runQuery('UPDATE users set name=? WHERE id=?',(name,userid)).addCallback(lambda x: ws.maj(["user/%s" % userid],userid,iduser))
		else:
			password=hashlib.md5(password).hexdigest()
			return db.connexion.runQuery('UPDATE users set name=?, password=? WHERE id=?',(name,password,userid)).addCallback(lambda x: ws.maj(["user/%s" % userid],userid,iduser))
	return False
def del_group(groupid, iduser):
	if iduser==1:
		return db.connexion.runQuery("DELETE FROM groups WHERE id=?",(groupid,)).addCallback(lambda x: ws.maj(["group/%s" % groupid],groupid,iduser))
	return False
def do_add_group(txn,nom,iduser):
	txn.execute('INSERT INTO groups (nom) VALUES (?)',(nom,))
	return txn.lastrowid
def add_group(nom,iduser):
	if iduser==1:
		return db.connexion.runInteraction(this.do_add_group, nom, iduser).addCallback(lambda groupid: ws.maj(["group/%s" % groupid],groupid,iduser))
def mod_group(groupid,nom,iduser):
	if iduser==1:
		return db.connexion.runQuery('UPDATE groups set nom=? WHERE id=?',(nom,groupid)).addCallback(lambda x: ws.maj(["group/%s" % groupid],groupid,iduser))
	return False
def add_user_group(userid,groupid,iduser):
	if iduser==1:
		return db.connexion.runQuery('INSERT OR REPLACE INTO user_group (id_user,id_group) VALUES (?,?)',(userid,groupid)).addCallback(lambda x: ws.maj(["*"],groupid,iduser))
def del_user_group(userid,groupid,iduser):
	if iduser==1:
		return db.connexion.runQuery('DELETE FROM user_group WHERE id_user=? AND id_group=?',(userid,groupid)).addCallback(lambda x: ws.maj(["*"],groupid,iduser))
def add_acl(type_ressource,id_ressource,type_acces,id_acces,level,iduser):
	return db.connexion.runQuery("INSERT OR REPLACE INTO acl (type_ressource, id_ressource, type_acces, id_acces, level) SELECT ?,?,?,?,? WHERE ?=1 OR (? in (SELECT createdby FROM {} WHERE id=?))".format(type_ressource),(type_ressource,id_ressource,type_acces,id_acces,level,iduser,iduser,id_ressource)).addCallback(lambda x: ws.maj(["*"],iduser,iduser));
def is_allowed(type_ressource,id_ressource,level,iduser):
	return db.connexion.runQuery("SELECT 1 from {} WHERE id=? AND ( ?=1 OR createdby=? OR id IN (SELECT id_ressource from acl where type_ressource=? AND type_acces='group' AND id_acces IN (select id_group from user_group where id_user=?)))".format(type_ressource),(id_ressource,iduser,iduser,type_ressource,iduser)).addCallback(lambda x: len(x)==1)
def del_acl(type_ressource,id_ressource,type_acces,id_acces,level,iduser):
	return db.connexion.runQuery("DELETE FROM acl WHERE type_ressource=? AND id_ressource=? AND type_acces=? AND id_acces=? AND level=? AND (?=1 OR (? in (SELECT createdby FROM {} WHERE id=?)))".format(type_ressource),(type_ressource,id_ressource,type_acces,id_acces,level,iduser,iduser,id_ressource)).addCallback(lambda x: ws.maj(["*"],iduser,iduser));

