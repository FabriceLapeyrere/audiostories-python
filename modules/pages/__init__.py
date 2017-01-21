from db import DB
from ws import maj
import json, time 
class Pages(object):
	def __init__(self):
		db = DB()
		self.connexion=db.connexion
	def build_page(self, dbentries):
		page=dbentries[0]
		page['verrou']=LinkRouter().get_verrou('page/%s' % (page['id']))
		return page
	def build_pages(self,dbentries):
		pages=[]
		for row in dbentries:
			pages.append(self.build_page([row]))
		return pages
	def get_page(self, idpage, iduser):
		return self.connexion.runQuery("SELECT * FROM pages WHERE id=?", (idpage,)).addCallback(self.build_page)
	def get_page_pub(self, idpage, iduser):
		return self.connexion.runQuery("SELECT * FROM pages WHERE id=? AND statut=1", (idpage,)).addCallback(lambda x: x[0])
	def get_pages(self, iduser):
		return self.connexion.runQuery("SELECT * FROM pages").addCallback(self.build_pages)
	def get_pages_pub(self, iduser):
		return self.connexion.runQuery("SELECT * FROM pages WHERE statut=1").addCallback(lambda x: x)
	def do_mod_page(self,txn,params,iduser):
		now=int(time.time()*1000.0)
		idpage=params.get('id','')
		nom=params.get('nom','')
		html=params.get('html','')
		statut=params.get('statut',0)
		txn.execute('UPDATE pages SET nom=?, html=?, statut=?, modificationdate=?, modifiedby=? WHERE id=?',(nom, html, statut, now, iduser,idpage))
		return idpage
	def mod_page(self,params,iduser):
		return self.connexion.runInteraction(self.do_mod_page, params, iduser).addCallback(lambda idpage: maj(["page/%s" % idpage],idpage,iduser))
	def do_del_page(self,txn,params,iduser):
		idpage=params['page']['id']
		page=params['page']
		now=int(time.time()*1000.0)
		txn.execute('INSERT INTO trash (id_item, type, json, date , by) VALUES (?,?,?,?,?) ',(idpage,'page',json.dumps(page),now,iduser))
		txn.execute('DELETE FROM pages WHERE id=? ', (idpage,))
		return idpage
	def del_page(self,params,iduser):
		return self.connexion.runInteraction(self.do_del_page, params, iduser).addCallback(lambda idpage: maj(["page/%s" % idpage],idpage,iduser))
	def do_add_page(self,txn,params,iduser):
		nom=params['page']['nom']
		now=int(time.time()*1000.0)
		txn.execute('INSERT INTO pages (nom, html, statut, creationdate, createdby, modificationdate, modifiedby) VALUES (?,?,?,?,?,?,?)',(nom, '', 0, now, iduser, now, iduser))
		return txn.lastrowid
	def add_page(self,params,iduser):
		return self.connexion.runInteraction(self.do_add_page, params, iduser).addCallback(lambda idpage: maj(["page/%s" % idpage],idpage,iduser))
