from jinja2 import Template, Environment, PackageLoader
from twisted.web.server import NOT_DONE_YET
from twisted.internet import defer
from twisted.web.resource import Resource
from twisted.web.static import File
from login import current_user
import json
import modules.stories
import modules.constantes

env = Environment(loader=PackageLoader('admin','templates'))
def html_image_vide(taille):
	w=int(modules.constantes.conf['miniatures'][taille])
	h=int(w/modules.constantes.conf['ratio'])
	return "<img class='img-responsive' width='%s' height='%s'>" % (w,h)
def html_image(f,idstory):
	return "<img class='img-responsive' src='%s/files/%s'>" % (idstory,f);
def html_image_index(f,idgroup,idstory):
	return "<img class='img-responsive' src='%s/story/%s/files/%s'>" % (idgroup,idstory,f);
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
	def __init__(self, idgroup=0):
		Resource.__init__(self)
		self.idgroup = idgroup
	def getChild(self, name, request):
		user = current_user(request)
		idstory=int(name)
		iduser=user['uid']
		idgroup=self.idgroup
		s=Previsuid(idstory,idgroup,iduser)
		s.putChild('lib',File("public/lib", "application/javascript"))
		s.putChild('css',File("public/css", "application/javascript"))
		s.putChild('js',File("public/js", "application/javascript"))
		s.putChild('img',File("public/img", "application/javascript"))
		s.putChild('files',File("data/files/story/%s" % (idstory), "application/javascript"))
		return s
	def render_GET(self, request):
		return redirectTo('/admin', request)
class PrevisuGroup(Resource):
	isLeaf = False
	def getChild(self, name, request):
		user = current_user(request)
		idgroup=int(name)
		iduser=user['uid']
		s=PrevisuGroupid(idgroup,iduser)
		s.putChild('lib',File("public/lib", "application/javascript"))
		s.putChild('css',File("public/css", "application/javascript"))
		s.putChild('js',File("public/js", "application/javascript"))
		s.putChild('img',File("public/img", "application/javascript"))
		s.putChild('story',Previsu(idgroup))
		return s
	def render_GET(self, request):
		return redirectTo('/admin', request)
class PrevisuGroupid(Resource):
	isLeaf = False
	def __init__(self, idstory, iduser):
		Resource.__init__(self)
		self.idgroup = idstory
		self.iduser = iduser
	def render_GET(self, request):
		dl = defer.DeferredList([modules.stories.get_stories_group(self.idgroup,self.iduser)])
		dl.addCallback(self._delayedRender,request)
		return NOT_DONE_YET
	def _delayedRender(self, res, request):
		if len(res[0][1])>0:
			ctx = {}
			ctx['idgroup'] = self.idgroup
			ctx['stories'] = res[0][1]
			ctx['ratio'] = modules.constantes.conf['ratio']
			ctx['pages'] = []
			template = env.get_template("previsu_group.html")
			request.write(template.render(ctx).encode('utf-8'))
			request.finish()
		else:
			request.redirect('/admin')
			request.finish()
class Previsuid(Resource):
	isLeaf = False
	def __init__(self, idstory, idgroup, iduser):
		Resource.__init__(self)
		self.idstory = idstory
		self.idgroup = idgroup
		self.iduser = iduser
	def render_GET(self, request):
		dl = defer.DeferredList([modules.stories.get_story(self.idstory,self.iduser), modules.stories.get_stories_group(self.idgroup,self.iduser)])
		dl.addCallback(self._delayedRender,request)
		return NOT_DONE_YET
	def _delayedRender(self, res, request):
		if 'id' in res[0][1]:
			ctx = {}
			ctx['idgroup'] = self.idgroup
			ctx['story'] = res[0][1]
			ctx['stories'] = res[1][1]
			ctx['ratio'] = modules.constantes.conf['ratio']
			ctx['pages'] = []
			template = env.get_template("previsu.html")
			request.write(template.render(ctx).encode('utf-8'))
			request.finish()
		else:
			request.redirect('/admin')
			request.finish()

