import db, ws, sys, json, time 

this = sys.modules[__name__]

def build_page( dbentries):
	page=dbentries[0]
	page['verrou']=ws.get_verrou('page/%s' % (page['id']))
	return page
def build_pages(dbentries):
	pages=[]
	for row in dbentries:
		pages.append(this.build_page([row]))
	return pages
def get_page( idpage, iduser):
	return db.connexion.runQuery("SELECT * FROM pages WHERE id=?", (idpage,)).addCallback(this.build_page)
def get_page_pub( idpage, iduser):
	return db.connexion.runQuery("SELECT * FROM pages WHERE id=? AND statut=1", (idpage,)).addCallback(lambda x: {} if len(x)==0 else x[0])
def get_pages( iduser):
	return db.connexion.runQuery("SELECT * FROM pages").addCallback(this.build_pages)
def get_pages_pub( iduser):
	return db.connexion.runQuery("SELECT * FROM pages WHERE statut=1").addCallback(lambda x: x)
def do_mod_page(txn,params,iduser):
	now=int(time.time()*1000.0)
	idpage=params.get('id','')
	nom=params.get('nom','')
	html=params.get('html','')
	statut=params.get('statut',0)
	txn.execute('UPDATE pages SET nom=?, html=?, statut=?, modificationdate=?, modifiedby=? WHERE id=?',(nom, html, statut, now, iduser,idpage))
	return idpage
def mod_page(params,iduser):
	return db.connexion.runInteraction(this.do_mod_page, params, iduser).addCallback(lambda idpage: ws.maj(["page/%s" % idpage],idpage,iduser))
def do_del_page(txn,params,iduser):
	idpage=params['page']['id']
	page=params['page']
	now=int(time.time()*1000.0)
	txn.execute('INSERT INTO trash (id_item, type, json, date , by) VALUES (?,?,?,?,?) ',(idpage,'page',json.dumps(page),now,iduser))
	txn.execute('DELETE FROM pages WHERE id=? ', (idpage,))
	return idpage
def del_page(params,iduser):
	return db.connexion.runInteraction(this.do_del_page, params, iduser).addCallback(lambda idpage: ws.maj(["page/%s" % idpage],idpage,iduser))
def do_add_page(txn,params,iduser):
	nom=params['page']['nom']
	now=int(time.time()*1000.0)
	txn.execute('INSERT INTO pages (nom, html, statut, creationdate, createdby, modificationdate, modifiedby) VALUES (?,?,?,?,?,?,?)',(nom, '', 0, now, iduser, now, iduser))
	return txn.lastrowid
def add_page(params,iduser):
	return db.connexion.runInteraction(this.do_add_page, params, iduser).addCallback(lambda idpage: ws.maj(["page/%s" % idpage],idpage,iduser))
