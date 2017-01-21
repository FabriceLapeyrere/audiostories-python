from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
import hashlib, json, sys, router, Cookie
from twisted.internet import defer

this = sys.modules[__name__]

def get_context(context):
	ctype=context['type']
    	params=context['params']
	iduser=params['iduser']
	c=this.get_cache(context)
	res={}
	if c!=False:
		res=c;
		print("%s from cache" % ctype)
		return defer.maybeDeferred(lambda: res)
	else:
		tab=ctype.split('/')
		res=router.gets(tab,res,iduser)
		res=defer.maybeDeferred(lambda: res)
		res.addCallback(this.set_cache,context)
		return res

def deps(ctype):
	tab=ctype.split('/')
	res=[ctype]
	res=router.deps(tab,res)
	return res

def maj(types,value,iduser):
	res=[]
	for ctype in types:
		for t in this.get_sub_contexts(ctype):
			res=res + this.deps(t);
	res=list(set((res)))
	this.del_cache(res)
	this.notify_all(res,iduser)
	return value
def notify_context(data,peer,context):
	ctype=context['type']
    	modele={}
	key=hashlib.md5(json.dumps(context['params'])).hexdigest()
	k="%s-%s-%s" % (peer, ctype, key)
	if k in this.notified:
		notified=this.notified[k]
	else:
		notified=False
	if json.dumps(data)!=json.dumps(notified):
		this.notified[k]=data
		modele[ctype]=data
		print(":::: %s :::: notify => %s" % (peer, ctype))
		this.wsfactory.update_contexts(peer,modele)
	else:
		print(":::: %s :::: notify => %s not needed" % (peer, ctype))
def notify(peer,iduser):
	for context in this.subs[peer]['contexts']:
		this.get_context(context).addCallback(this.notify_context,peer,context)
def notify_all(types,iduser):
	for peer,sub in this.subs.items():
		test=False
		for c in sub['contexts']:
			if c['type'] in types:
				test=True
		if test:
			this.notify(peer,iduser)
def del_cache(types):
	for t in types:
		try:
			del this.cache[t]
		except:
			pass
def del_cache_all():
	this.cache={}
def get_cache(context):
	t=context['type']
	params=context['params']
	key=hashlib.md5(json.dumps(params)).hexdigest()
	try:
		return this.cache[t][key]
	except:
		return False
def set_cache(data,context):
	t=context['type']
	params=context['params']
	key=hashlib.md5(json.dumps(params)).hexdigest()
	if not t in this.cache:
		this.cache[t]={}
	this.cache[t][key]=data
	print("%s computed" % t)
	return data
def contexts_update(peer,contexts,iduser):
	res=[]
	for c in contexts:
		c['params']['iduser']=iduser
		if 'force' in c:
			ctype=c['type']
		    	key=hashlib.md5(json.dumps(c['params'])).hexdigest()
			k="%s-%s-%s" % (peer, ctype, key)
			try:
				del this.notified[k]
			except:
				pass
		res.append(c)
	this.subs[peer]['contexts']=res
	print(":::: %s :::: contexts update %s item(s)" % (peer, len(res)));
	this.notify(peer,iduser);
def get_sub_contexts(filtre):
	print(filtre)
	res=[]
	tab=filtre.split('/');
	print(tab)
	if len(tab)>1 and tab[1]=='*':
		this.del_cache_all()
		for peer,sub in this.subs.items():
			for c in sub['contexts']:
				tabc=c['type'].split('/')
				if tab[0]==tabc[0]:
					res.append(c['type'])
	elif filtre=='*':
		this.del_cache_all()
		for peer,sub in this.subs.items():
			for c in sub['contexts']:
				res.append(c['type'])
	else:
		res.append(filtre)
	return res
def set_verrou(peer,ctype,iduser):
	print(":::: %s :::: set verrou %s" % (peer,ctype))
	this.verrous[ctype]=peer
	this.maj([router.context_verrou(ctype)],0,iduser)
def del_verrou(peer,ctype,iduser):
	print(":::: %s :::: del verrou %s" % (peer,ctype))
	del this.verrous[ctype]
	this.maj([router.context_verrou(ctype)],0,iduser)
def del_verrous_peer(peer,iduser):
	print(":::: %s :::: del verrous" % (peer,ctype))
	for ctype,p in this.verrous:
		if p==peer:
			del this.verrous[ctype]
	this.maj([router.context_verrou(ctype)],0,iduser)
def get_verrou(ctype):
	return this.verrous.get(ctype,'none')

class LinkServerProtocol(WebSocketServerProtocol):
	def onConnect(self, request):
		cookie = Cookie.SimpleCookie()
		cookie.load(request.headers['cookie'].encode("utf8"))
		uid = cookie['TWISTED_SESSION'].value
		print("WebSocket connection request: {}".format(uid))
		self.factory.register(self,uid)

	def connectionLost(self, reason):
		WebSocketServerProtocol.connectionLost(self, reason)
		print("WebSocket connection closed: {}".format(self.peer))
		self.factory.unregister(self)
		
	def onMessage(self, payload, isBinary):
		print("WebSocket message: {}".format(self.peer))
		for uid in this.logged:
			if self.peer in this.logged[uid]['peers']:
				self.factory.site.getSession(uid).touch()
				iduser=this.logged[uid]['userid']
				print("message: {}".format(payload))
				m=json.loads(payload)
				for action in m:
					if action['action']=='update_contexts':
						this.contexts_update(self.peer,action['contexts'],iduser)
					if action['action']=='set_verrou':
						this.set_verrou(self.peer,action['verrou'],iduser)
					if action['action']=='del_verrou':
						this.del_verrou(self.peer,action['verrou'],iduser)
class LinkServerFactory(WebSocketServerFactory):
	"""
	Link router to all
	currently connected clients.
	"""
	def __init__(self):
		WebSocketServerFactory.__init__(self)
		self.clients = {}

	def register(self, client, uid):
		if client.peer not in self.clients:
			peer=client.peer
			print("registered client %s" % peer)
			self.clients[peer]=client
			this.logged[uid]['peers'].append(peer)
			this.peers[peer]={'uid':uid,'userid':this.logged[uid]['userid']}
			this.subs[peer]={'userid':this.logged[uid]['userid'],'contexts':[]}
		self.broadcast({'type':'modele','collection':{'logged':this.logged,'peers':this.peers}})


	def unregister(self, client):
		if client.peer in self.clients:
			peer=client.peer
			print("unregistered client %s" % peer)
			del self.clients[peer]
			del this.peers[peer]
			for k,v in this.verrous.items():
				if v==peer:
					LinkRouter().del_verrou(peer,k,1)
			for i in this.logged:
				if peer in this.logged[i]['peers']:
					this.logged[i]['peers'].remove(peer)
			del this.subs[peer]
		self.broadcast({'type':'modele','collection':{'logged':this.logged,'peers':this.peers}})
	def broadcast(self, m):
		msg=json.dumps(m)
		print("broadcasting message...")
		for p,c in self.clients.items():
			c.sendMessage(msg.encode('utf8'))
			print("message sent to {}".format(c.peer))
	def update_contexts(self, peer, modele):
		modele['myid']=this.peers[peer]['userid']
		modele['mypeer']=peer
		modele['peers']=this.peers
		modele['logged']=this.logged
		m={'type':'modele','collection':modele}
		msg=json.dumps(m)
		for p,c in self.clients.items():
			if p==peer:
				c.sendMessage(msg.encode('utf8'))
				print("%s, modele update" % peer)
	def logout(self,uid):
		print("session expired !! %s" % uid)
		msg=json.dumps({'type':'logout'})
		if uid in this.logged:
			for p in this.logged[uid]['peers']:
				for peer,c in self.clients.items():
					if peer==p:
						c.sendMessage(msg.encode('utf8'))
						print("message sent to {}".format(c.peer))
						c.sendClose()
						print("close connexion with {}".format(c.peer))
			del this.logged[uid]	

this.notified={}
this.cache={}
this.subs={}
this.verrous={}
this.peers={}
this.logged={}
this.wsfactory = this.LinkServerFactory()
this.wsfactory.protocol = this.LinkServerProtocol

