from jinja2 import Template, Environment, PackageLoader
from twisted.web.server import NOT_DONE_YET
from twisted.internet import defer
from twisted.web.resource import Resource, NoResource
from twisted.web.static import File
import json
import modules.stories
import modules.constantes

env = Environment(loader=PackageLoader('public','templates'))
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

class Selection(Resource):
	isLeaf = False
	def __init__(self, name, sel):
		Resource.__init__(self)
		self.name = name
		self.sel = sel
	def getChild(self, name, request):
		idstory=int(name)
		s=Selectionid(idstory,self.name,self.sel,1)
		s.putChild('lib',File("public/lib", "application/javascript"))
		s.putChild('css',File("public/css", "application/javascript"))
		s.putChild('js',File("public/js", "application/javascript"))
		s.putChild('img',File("data/img", "application/javascript"))
		s.putChild('files',File("data/files/story/%s" % (idstory), "application/javascript"))
		return s
	def render_GET(self, request):
		return NoResource("No such resource.").render()
class SelectionGroup(Resource):
	isLeaf = False
	def getChild(self, name, request):
		if 'selections' not in modules.constantes.conf:
			return NoResource("No such resource.")
		if name in modules.constantes.conf['selections']:
			sel=modules.constantes.conf['selections'][name]
			s=SelectionGroupid(name,sel,1)
			s.putChild('lib',File("public/lib", "application/javascript"))
			s.putChild('css',File("public/css", "application/javascript"))
			s.putChild('js',File("public/js", "application/javascript"))
			s.putChild('img',File("data/img", "application/javascript"))
			s.putChild('story',Selection(name,sel))
			return s
		else:
			return NoResource("No such resource.")
	def render_GET(self, request):
		return NoResource("No such resource.").render()
class SelectionGroupid(Resource):
	isLeaf = False
	def __init__(self, name, sel, iduser):
		Resource.__init__(self)
		self.name=name
		self.sel=sel
		self.iduser = iduser
	def render_GET(self, request):
		dl = defer.DeferredList([modules.stories.get_stories_group(self.sel['idgroup'],self.iduser)])
		dl.addCallback(self._delayedRender,request)
		return NOT_DONE_YET
	def _delayedRender(self, res, request):
		if len(res[0][1])>0:
			ctx = {}
			ctx['name'] = self.name
			ctx['sel'] = self.sel
			ctx['stories'] = res[0][1]
			ctx['ratio'] = modules.constantes.conf['ratio']
			ctx['pages'] = []
			ctx['footer'] = ''
			template = env.get_template("selection_group.html")
			request.write(template.render(ctx).encode('utf-8'))
			request.finish()
		else:
			return NoResource("No such resource.").render()
class Selectionid(Resource):
	isLeaf = False
	def __init__(self, idstory, name, sel, iduser):
		Resource.__init__(self)
		self.idstory = idstory
		self.name = name
		self.sel = sel
		self.iduser = iduser
	def render_GET(self, request):
		print("###### %s ######" % self.sel)
		dl = defer.DeferredList([modules.stories.get_story(self.idstory,self.iduser), modules.stories.get_stories_group(self.sel['idgroup'],self.iduser)])
		dl.addCallback(self._delayedRender,request)
		return NOT_DONE_YET
	def _delayedRender(self, res, request):
		if 'id' in res[0][1]:
			ctx = {}
			for i in range(len(res[1][1])):
				if res[1][1][i]['id']==res[0][1]['id']:
					del res[1][1][i]
					break
			ctx['name'] = self.name
			ctx['sel'] = self.sel
			ctx['story'] = res[0][1]
			ctx['stories'] = res[1][1]
			ctx['ratio'] = modules.constantes.conf['ratio']
			ctx['pages'] = []
			ctx['footer'] = ''
			template = env.get_template("selection.html")
			request.write(template.render(ctx).encode('utf-8'))
			request.finish()
		else:
			return NoResource("No such resource.").render()

