import admin, hashlib, json, modules, config
from twisted.internet import defer
class LinkRouter(object):
	def get_context(self,context):
		ctype=context['type']
	    	params=context['params']
		iduser=params['iduser']
		c=self.get_cache(context)
		res={}
		if c!=False:
			res=c;
			print("%s from cache" % ctype)
			return defer.maybeDeferred(lambda: res)
		else:
			tab=ctype.split('/')
			res=modules.gets(tab,res,iduser)
			res=defer.maybeDeferred(lambda: res)
			res.addCallback(self.set_cache,context)
			return res
	def context_verrou(self,ctype):
		tab=ctype.split('/')
		print("context verrou %s" % ctype)
		if tab[0]=="user":
			return 'users'
		if tab[0]=="group":
			return 'groups'
		if tab[0]=="page":
			return 'pages'
		if "story_" in tab[0]:
			return 'story/%s' % tab[1]
		return ctype;

	def deps(self,ctype):
		tab=ctype.split('/')
		res=[ctype]
		res=modules.deps(tab,res)
		return res

	def maj(self,types,value,iduser):
		res=[]
		for ctype in types:
			for t in self.get_sub_contexts(ctype):
				res=res + self.deps(t);
		res=list(set((res)))
		self.del_cache(res)
		self.notify_all(res,iduser)
		return value
	def notify_context(self,data,peer,context):
		ctype=context['type']
	    	modele={}
		key=hashlib.md5(json.dumps(context['params'])).hexdigest()
		k="%s-%s-%s" % (peer, ctype, key)
		if k in admin.notified:
			notified=admin.notified[k]
		else:
			notified=False
		if json.dumps(data)!=json.dumps(notified):
			admin.notified[k]=data
			modele[ctype]=data
			print(":::: %s :::: notify => %s" % (peer, ctype))
			admin.wsfactory.update_contexts(peer,modele)
		else:
			print(":::: %s :::: notify => %s not needed" % (peer, ctype))
	def notify(self,peer,iduser):
		for context in admin.subs[peer]['contexts']:
			self.get_context(context).addCallback(self.notify_context,peer,context)
	def notify_all(self,types,iduser):
		for peer,sub in admin.subs.items():
			test=False
			for c in sub['contexts']:
				if c['type'] in types:
					test=True
			if test:
				self.notify(peer,iduser)
	def del_cache(self,types):
		for t in types:
			try:
				del admin.cache[t]
			except:
				pass
	def del_cache_all(self):
		admin.cache={}
	def get_cache(self,context):
		t=context['type']
		params=context['params']
		key=hashlib.md5(json.dumps(params)).hexdigest()
		try:
			return admin.cache[t][key]
		except:
			return False
	def set_cache(self,data,context):
		t=context['type']
		params=context['params']
		key=hashlib.md5(json.dumps(params)).hexdigest()
		if not t in admin.cache:
			admin.cache[t]={}
		admin.cache[t][key]=data
		print("%s computed" % t)
		return data
	def contexts_update(self,peer,contexts,iduser):
		res=[]
		for c in contexts:
			c['params']['iduser']=iduser
			if 'force' in c:
				ctype=c['type']
			    	key=hashlib.md5(json.dumps(c['params'])).hexdigest()
				k="%s-%s-%s" % (peer, ctype, key)
				try:
					del admin.notified[k]
				except:
					pass
			res.append(c)
		admin.subs[peer]['contexts']=res
		print(":::: %s :::: contexts update %s item(s)" % (peer, len(res)));
		self.notify(peer,iduser);
	def get_sub_contexts(self,filtre):
		print(filtre)
		res=[]
		tab=filtre.split('/');
		print(tab)
		if len(tab)>1 and tab[1]=='*':
			self.del_cache_all()
			for peer,sub in admin.subs.items():
				for c in sub['contexts']:
					tabc=c['type'].split('/')
					if tab[0]==tabc[0]:
						res.append(c['type'])
		elif filtre=='*':
			self.del_cache_all()
			for peer,sub in admin.subs.items():
				for c in sub['contexts']:
					res.append(c['type'])
		else:
			res.append(filtre)
		return res
	def set_verrou(self,peer,ctype,iduser):
		print(":::: %s :::: set verrou %s" % (peer,ctype))
		admin.verrous[ctype]=peer
		self.maj([self.context_verrou(ctype)],0,iduser)
	def del_verrou(self,peer,ctype,iduser):
		print(":::: %s :::: del verrou %s" % (peer,ctype))
		del admin.verrous[ctype]
		self.maj([self.context_verrou(ctype)],0,iduser)
	def del_verrous_peer(self,peer,iduser):
		print(":::: %s :::: del verrous" % (peer,ctype))
		for ctype,p in admin.verrous:
			if p==peer:
				del admin.verrous[ctype]
		self.maj([self.context_verrou(ctype)],0,iduser)
	def get_verrou(self,ctype):
		return admin.verrous.get(ctype,'none')

