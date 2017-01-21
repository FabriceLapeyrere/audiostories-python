#
# Login Page logic using Twisted sessions
#
# Defines two functions used like before filters
#   current_user(reqeust) - return the name or ""
#   require_login(request) - go to login page if not logged in
#
# LoginResource()
# LogoutResource()
# IndexResource({ dict })
#
# pip install Jinja2
# python -m muet.login_logic_jinga2

import sys, cgi, random, hashlib, ws, db
import modules.constantes

from twisted.web.server import Site, NOT_DONE_YET
from twisted.web import static
from twisted.web.resource import Resource
from twisted.internet import reactor

from zope.interface import Interface, Attribute, implements
from twisted.web.server import Session
from twisted.python import log
from twisted.python.components import registerAdapter

from jinja2 import Template, Environment, PackageLoader
env = Environment(loader=PackageLoader('admin','templates')) # templates dir under muet package

#
# Access to session data is through a componentized interface
#

class IAvatarSessionData(Interface):
	prefs = Attribute("the users preferences")
	userid = Attribute("the users id")
	name = Attribute("the users name")
	login = Attribute("the users login")
	csrf = Attribute("the csrf token")
	urlref = Attribute("where to go after login")

class AvatarSessionData(object):
	implements(IAvatarSessionData)

	def __init__(self, session):
		self.prefs = ""
		self.userid = ""
		self.name = ""
		self.login = ""
		self.csrf = ""
		self.urlref = ""

registerAdapter(AvatarSessionData, Session, IAvatarSessionData)

#
# get the current user from the session
#

def current_user(request):
	session = request.getSession()
	avatar = IAvatarSessionData(session)
	user = { 'login':avatar.login, 'name':avatar.name, 'uid':avatar.userid}
	print "CURRENT_USER:%s" % user['login']
	return user

#
# guard a page and redirect if not logged in
#

def require_login(request):
	urlref = request.path
	print "REQUIRE_LOGIN:%s" % urlref

	session = request.getSession()
	avatar = IAvatarSessionData(session)
	print "DOING REDIRECT"
	request.redirect("/admin/login?_urlref=%s" % urlref)
	request.finish()
	return NOT_DONE_YET

#
# This is a very simple login page
#
	
class LoginPage(Resource):

	def __init__(self):
		Resource.__init__(self)

	# unconditionally render the login page
	def render_GET(self, request):
		session = request.getSession()
		avatar = IAvatarSessionData(session)
		if avatar.csrf=="":
			avatar.csrf = str(random.randint(0, 1000000))
		if "_urlref" in request.args:
			urlref=cgi.escape(request.args["_urlref"][0],)
		else :
			urlref="/admin/stories"
		ctx = {
			'brand' : modules.constantes.conf['brand'],
			'_urlref' : urlref,
			'_csrf' : avatar.csrf
			}
		template = env.get_template("login_greeting.html")

		return str(template.render(ctx).encode('utf-8'))

	#
	# The following section implements the callback chain for login database query
	#

	def onResult(self, dbdata, request, login, password, urlref):

		log.msg("On Result:%s %s %s" % (dbdata, login, password))

		dbUserLogin = ""
		dbUserPassword = ""
		dbUserName = ""
		dbUserUid = ""
		dbUserPrefs = ""
		success = False
		if len(dbdata) != 0:
			dbUserLogin = dbdata[0]['login']
			dbUserPassword = dbdata[0]['password']
			dbUserName = dbdata[0]['name']
			dbUserUid = dbdata[0]['id']

			if hashlib.md5(password).hexdigest() == dbUserPassword:
				success = True

		if success:
			session = request.getSession()
			session.notifyOnExpire(lambda: ws.wsfactory.logout(session.uid))
			avatar = IAvatarSessionData(session)
			avatar.login = login
			avatar.name = dbUserName
			avatar.userid = dbUserUid
			avatar.prefs = dbUserPrefs
			ws.logged[session.uid]={'userid':dbUserUid, 'peers':[]}
			log.msg("AVATAR uid : %s" % session.uid)
			
			request.redirect(urlref)
			request.finish()
			pass

		else:
			request.redirect("/admin/login")
			request.finish()

	#
	# Retrieve the name/password post data and start the database query
	#

	def render_POST(self, request):
		session = request.getSession()
		avatar = IAvatarSessionData(session)

		# retrieve from post data
		login = cgi.escape(request.args["login"][0],)
		password = cgi.escape(request.args["password"][0],)
		csrf = cgi.escape(request.args["_csrf"][0],)
		urlref = cgi.escape(request.args["_urlref"][0],)
		
		log.msg("POST csrf:%s login:%s password:%s" % (csrf, login, password))

		if csrf != avatar.csrf:
			log.msg("CSRF ATTACK!")
			request.redirect("/admin/login")
			request.finish()
			return NOT_DONE_YET
			

		# Run the query
		d = db.connexion.runQuery("SELECT login, password, name, id, prefs from users WHERE login = ? and active = 1 LIMIT 1", (login,))
		d.addCallback(self.onResult, request, login, password, urlref)

		return NOT_DONE_YET


class Protected(Resource):
	def __init__(self,resource):
		Resource.__init__(self)
		self.resource=resource

	def render_GET(self, request):
		user = current_user(request)
		if not user['login']:
			return require_login(request)
		return self.resource.render_GET(request)
	def render_POST(self, request):
		user = current_user(request)
		if not user['login']:
			return require_login(request)
		return self.resource.render_POST(request)
	def getChild(self, path, request):
		user = current_user(request)
		if not user['login']:
			return self
		return self.resource.getChild(path, request)
			
		
class LogoutPage(Resource):

	def render_GET(self, request):
		session=request.getSession()
		request.getSession().expire()
		print(request.args)
		if 'url' in request.args:
			request.redirect(request.args['url'][0])
			request.finish()
			return NOT_DONE_YET	
		ctx = {}
		template = env.get_template("logout_greeting.html")
		return str(template.render(ctx).encode('utf-8'))

#
# Every site should have a main index.html
#  This is also the outline of how every page protects itself.
#

class IndexPage(Resource):
	
	isLeaf = True

	def __init__(self):
		Resource.__init__(self)

	def render_GET(self, request):
		user = current_user(request)
		# add the user to the context
		ctx = {}
		ctx['brand'] =  modules.constantes.conf['brand']
		ctx['ratio'] = 100/ modules.constantes.conf['ratio']
		ctx['user_name'] = user['name']
		ctx['user_login'] = user['login']
		ctx['user_id'] = user['uid']
		template = env.get_template("index.html")
		return str(template.render(ctx).encode('utf-8'))

#
# The root page usually wants to redirect to somewhere else
#

class RootPage(Resource):

	def render_GET(self, request):
		log.msg("ROOT REDIRECT")
		request.redirect("/admin/index")
		request.finish()
		return NOT_DONE_YET
	def getChild(self, path, request):
		if path in ["","stories","admin","pages","moi","addpage","adduser","addgroup"]:
			return Protected(IndexPage())
		if path in ["modpage","modstory","moduser","modgroup"]:
			return AngularRoute()
		return self
class AngularRoute(Resource):
	def render_GET(self, request):
		log.msg("ROOT REDIRECT")
		request.redirect("/admin/index")
		request.finish()
		return NOT_DONE_YET
	def getChild(self, path, request):
		return Protected(IndexPage())			

