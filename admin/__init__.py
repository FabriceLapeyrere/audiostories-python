from zope.interface import implements
from twisted.python import log
from twisted.web.resource import IResource, Resource
from twisted.web.static import File
from twisted.web import rewrite
from login import Protected, IndexPage, LoginPage, LogoutPage, RootPage, current_user
from ws import LinkServerProtocol, LinkServerFactory
from router import LinkRouter
from ajax import Ajax
from upload import Upload
from autobahn.twisted.websocket import WebSocketServerFactory
from autobahn.twisted.resource import WebSocketResource
import os, glob
from twisted.web.util import redirectTo
from previsu import Previsu

dataok=False
peers={}
logged={}
notified={}
cache={}
subs={}
verrous={}
wsfactory = LinkServerFactory()
wsrouter = LinkRouter()
class Admin(object):
	def __init__(self, site):
		myroot = RootPage()
		wsfactory.protocol = LinkServerProtocol
		wsfactory.site = site
		wsresource = WebSocketResource(wsfactory)
		myroot.putChild("index", Protected(IndexPage()))
		myroot.putChild("login", LoginPage())
		myroot.putChild("logout", LogoutPage())
		myroot.putChild("img", File("admin/core/img", "application/javascript"))
		myroot.putChild("partials", Protected(File("admin/core/partials", "application/javascript")))
		myroot.putChild("css", File("admin/core/css", "application/javascript"))
		myroot.putChild("lib", File("admin/core/lib", "application/javascript"))
		myroot.putChild("js", File("admin/core/js", "application/javascript"))
		myroot.putChild("files", Protected(File("data/files", "application/javascript")))
		myroot.putChild("ajax", Protected(Ajax()))
		myroot.putChild("previsu", Protected(Previsu()))
		myroot.putChild("upload", Protected(Upload()))
		myroot.putChild(b"ws", wsresource)
		for m in glob.iglob("admin/modules/*"):
			mod=os.path.basename(m)
			myroot.putChild("%s_partials" % mod, File("admin/modules/%s/partials" % mod, "application/javascript"))
		self.root=myroot
