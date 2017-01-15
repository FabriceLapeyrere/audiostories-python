from jinja2 import Template, Environment, PackageLoader
from twisted.web.server import NOT_DONE_YET
from twisted.internet import defer
from twisted.web.resource import Resource
from twisted.web.static import File
from login import current_user
from modules.stories import Stories
from config import conf
import json

env = Environment(loader=PackageLoader('admin','templates'))
def html_image_vide(taille):
	w=int(conf['miniatures'][taille])
	h=int(w/conf['ratio'])
	return "<img class='img-responsive' width='%s' height='%s'>" % (w,h)
def html_image(f,idstory):
	return "<img class='img-responsive' src='%s/files/%s'>" % (idstory,f);
def html_image_index(f,idstory):
	return "<img class='img-responsive' src='files/story/%s/%s'>" % (idstory,f);
def html_image_diap(f,idstory):
	return "<img class='img-responsive' data-src='%s/files/%s'>" % (idstory,f);
def html_background_image(f,idstory):
	return "style='background:url(%s/files/%s) no-repeat cover'" % (idstory,f);
def proportion(ratio):
	return 49.5*(1/ratio)
def tojson(o):
	return json.dumps(o)
env.filters['html_image_vide'] = html_image_vide
env.filters['html_image'] = html_image
env.filters['html_image_index'] = html_image_index
env.filters['html_image_diap'] = html_image_diap
env.filters['html_background_image'] = html_background_image
env.filters['proportion'] = proportion
env.filters['tojson'] = tojson

class Previsu(Resource):
	isLeaf = False
	def getChild(self, name, request):
		user = current_user(request)
		idstory=int(name)
		iduser=user['uid']
		s=Previsuid(idstory,iduser)
		s.putChild('lib',File("public/lib", "application/javascript"))
		s.putChild('css',File("public/css", "application/javascript"))
		s.putChild('js',File("public/js", "application/javascript"))
		s.putChild('img',File("public/img", "application/javascript"))
		s.putChild('files',File("data/files/story/%s" % (idstory), "application/javascript"))
		return s
	def render_GET(self, request):
		return redirectTo('/admin', request)
class Previsuid(Resource):
	isLeaf = False
	def __init__(self, idstory, iduser):
		Resource.__init__(self)
		self.idstory = idstory
		self.iduser = iduser
	def render_GET(self, request):
		S=Stories()
		dl = defer.DeferredList([S.get_story(self.idstory,self.iduser), S.get_stories(self.iduser)])
		dl.addCallback(self._delayedRender,request)
		return NOT_DONE_YET
	def _delayedRender(self, res, request):
		if 'id' in res[0][1]:
			ctx = {}
			ctx['story'] = res[0][1]
			ctx['stories'] = res[1][1]
			ctx['ratio'] = conf['ratio']
			ctx['pages'] = []
			template = env.get_template("previsu.html")
			request.write(template.render(ctx).encode('utf-8'))
			request.finish()
		else:
			request.redirect('/admin')
			request.finish()

