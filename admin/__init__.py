from zope.interface import implements
from twisted.python import log
from twisted.web.resource import IResource, Resource
from twisted.web.static import File
from twisted.web import rewrite
import  os, glob, login, upload, previsu, ajax, ws
from autobahn.twisted.resource import WebSocketResource
from twisted.web.util import redirectTo

dataok=False
class Admin(object):
	def __init__(self, site):
		myroot = login.RootPage()
		ws.wsfactory.site = site
		myroot.putChild("index", login.Protected(login.IndexPage()))
		myroot.putChild("login", login.LoginPage())
		myroot.putChild("logout", login.LogoutPage())
		myroot.putChild("img", File("admin/core/img", "application/javascript"))
		myroot.putChild("partials", login.Protected(File("admin/core/partials", "application/javascript")))
		myroot.putChild("css", File("admin/core/css", "application/javascript"))
		myroot.putChild("lib", File("admin/core/lib", "application/javascript"))
		myroot.putChild("js", File("admin/core/js", "application/javascript"))
		myroot.putChild("files", login.Protected(File("data/files", "application/javascript")))
		myroot.putChild("ajax", login.Protected(ajax.Ajax()))
		myroot.putChild("previsu", login.Protected(previsu.Previsu()))
		myroot.putChild("upload", login.Protected(upload.Upload()))
		myroot.putChild(b"ws", WebSocketResource(ws.wsfactory))
		for m in glob.iglob("modules/*"):
			mod=os.path.basename(m)
			myroot.putChild("%s_partials" % mod, File("modules/%s/partials" % mod, "application/javascript"))
		self.root=myroot
