from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
from twisted.web.server import Session
import json, admin, config, Cookie
from admin.modules import constantes
from router import LinkRouter
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
		for uid in admin.logged:
			if self.peer in admin.logged[uid]['peers']:
				self.factory.site.getSession(uid).touch()
				iduser=admin.logged[uid]['userid']
				print("message: {}".format(payload))
				m=json.loads(payload)
				for action in m:
					if action['action']=='update_contexts':
						LinkRouter().contexts_update(self.peer,action['contexts'],iduser)
					if action['action']=='set_verrou':
						LinkRouter().set_verrou(self.peer,action['verrou'],iduser)
					if action['action']=='del_verrou':
						LinkRouter().del_verrou(self.peer,action['verrou'],iduser)
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
			admin.logged[uid]['peers'].append(peer)
			admin.peers[peer]={'uid':uid,'userid':admin.logged[uid]['userid']}
			admin.subs[peer]={'userid':admin.logged[uid]['userid'],'contexts':[]}
		self.broadcast({'type':'modele','collection':{'logged':admin.logged,'peers':admin.peers,'config':config.conf,'constantes':constantes.data}})


	def unregister(self, client):
		if client.peer in self.clients:
			peer=client.peer
			print("unregistered client %s" % peer)
			del self.clients[peer]
			del admin.peers[peer]
			for k,v in admin.verrous.items():
				if v==peer:
					LinkRouter().del_verrou(peer,k,1)
			for i in admin.logged:
				if peer in admin.logged[i]['peers']:
					admin.logged[i]['peers'].remove(peer)
			del admin.subs[peer]
		self.broadcast({'type':'modele','collection':{'logged':admin.logged,'peers':admin.peers,'config':config.conf,'constantes':constantes.data}})
	def broadcast(self, m):
		msg=json.dumps(m)
		print("broadcasting message...")
		for p,c in self.clients.items():
			c.sendMessage(msg.encode('utf8'))
			print("message sent to {}".format(c.peer))
	def update_contexts(self, peer, modele):
		modele['myid']=admin.peers[peer]['userid']
		modele['mypeer']=peer
		modele['peers']=admin.peers
		modele['logged']=admin.logged
		modele['config']=config.conf
		modele['constantes']=constantes.data
		m={'type':'modele','collection':modele}
		msg=json.dumps(m)
		for p,c in self.clients.items():
			if p==peer:
				c.sendMessage(msg.encode('utf8'))
				print("%s, modele update" % peer)
	def logout(self,uid):
		print("session expired !! %s" % uid)
		msg=json.dumps({'type':'logout'})
		if uid in admin.logged:
			for p in admin.logged[uid]['peers']:
				for peer,c in self.clients.items():
					if peer==p:
						c.sendMessage(msg.encode('utf8'))
						print("message sent to {}".format(c.peer))
						c.sendClose()
						print("close connexion with {}".format(c.peer))
			del admin.logged[uid]	
		
