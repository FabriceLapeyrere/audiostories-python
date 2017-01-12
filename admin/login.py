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

import sys
import cgi
import random
import hashlib

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
import admin, config
from db import DB
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
	avatar.urlref = urlref

	print "DOING REDIRECT"
	request.redirect("/admin/login")
	request.finish()
	return NOT_DONE_YET

#
# This is a very simple login page
#
	
class LoginPage(Resource):

	def __init__(self):
		db = DB()			# the database connection
		self.connexion=db.connexion
		Resource.__init__(self)

	# unconditionally render the login page
	def render_GET(self, request):
		session = request.getSession()
		avatar = IAvatarSessionData(session)
		avatar.csrf = str(random.randint(0, 1000000))

		ctx = {
			'brand' : config.conf['brand'],
			'_csrf' : avatar.csrf
			}
		template = env.get_template("login_greeting.html")

		return str(template.render(ctx).encode('utf-8'))

	#
	# The following section implements the callback chain for login database query
	#

	def onResult(self, dbdata, request, login, password):

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
			session.notifyOnExpire(lambda: admin.wsfactory.logout(session.uid))
			avatar = IAvatarSessionData(session)
			avatar.login = login
			avatar.name = dbUserName
			avatar.userid = dbUserUid
			avatar.prefs = dbUserPrefs
			admin.logged[session.uid]={'userid':dbUserUid, 'peers':[]}
			log.msg("AVATAR uid : %s" % session.uid)
			# retrieve from session and reset
			urlref = avatar.urlref
			avatar.urlref = ""

			if urlref:
				request.redirect(urlref)
				request.finish()
			else:
				request.redirect("/admin/")
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

		log.msg("POST csrf:%s login:%s password:%s" % (csrf, login, password))

		if csrf != avatar.csrf:
			log.msg("CSRF ATTACK!")
			request.redirect("/admin/login")
			request.finish()
			return NOT_DONE_YET
			

		# Run the query
		d = self.connexion.runQuery("SELECT login, password, name, id, prefs from users WHERE login = ? and active = 1 LIMIT 1", (login,))
		d.addCallback(self.onResult, request, login, password)

		return NOT_DONE_YET


class LogoutPage(Resource):

	def render_GET(self, request):
		session=request.getSession()
		request.getSession().expire()

		ctx = {
			}
		template = env.get_template("logout_greeting.html")

		return str(template.render(ctx).encode('utf-8'))

#
# Every site should have a main index.html
#  This is also the outline of how every page protects itself.
#

class IndexPage(Resource):
	
	isLeaf = True

	def __init__(self, ctx):
		self.ctx = ctx
		Resource.__init__(self)

	def render_GET(self, request):
		user = current_user(request)
		if not user['login']:
			# this should store the current path, render the login page, and finally redirect back here
			return require_login(request)
		print('OK')
		# add the user to the context
		ctx = self.ctx.copy()
		ctx['brand'] = config.conf['brand']
		ctx['ratio'] = 100/config.conf['ratio']
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
