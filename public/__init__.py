from zope.interface import implements
from twisted.internet import defer
from twisted.web.resource import Resource, NoResource
from twisted.web.static import File
from twisted.web.server import NOT_DONE_YET
from jinja2 import Template, Environment, PackageLoader
from twisted.web import rewrite
from twisted.web.util import redirectTo, DeferredResource
import random, json, os
import modules.stories
import modules.pages
import modules.constantes
import selection

env = Environment(loader=PackageLoader('public','templates'))
def html_image_vide(taille):
	w=int(modules.constantes.conf['miniatures'][taille])
	h=int(w/modules.constantes.conf['ratio'])
	return "<img class='img-responsive' width='%s' height='%s'>" % (w,h)
def html_image(f,idstory):
	return "<img class='img-responsive' src='%s/files/%s'>" % (idstory,f);
def html_image_index(f,idstory):
	return "<img class='img-responsive' src='story/%s/files/%s'>" % (idstory,f);
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

class RootPage(Resource):
	isLeaf=False
	def __init__(self):
		Resource.__init__(self)
	def getChild(self, name, request):
		if name == '':
			return self
		return Resource.getChild(self, name, request)
	def render_GET(self, request):
		dl = defer.DeferredList([modules.stories.get_stories_pub(0),modules.pages.get_pages_pub(0)])
		dl.addCallback(self._delayedRender,request)
		return NOT_DONE_YET
	def _delayedRender(self, res, request):
		ctx = {}
		ctx['stories'] = res[0][1]
		ctx['brand'] = modules.constantes.conf['brand']
		ctx['pages'] = res[1][1]
		ctx['footer'] = ''
		f="data/footer.html"
		if os.path.isfile(f):
			ctx['footer'] = unicode(open(f, "r").read(), 'utf-8')
		template = env.get_template("index.html")
		request.write(template.render(ctx).encode('utf-8'))
		request.finish()
		
class Story(Resource):
	isLeaf = False
	def getChild(self, name, request):
		try:
			idstory=int(name)
		except:
			return self
		dl = defer.DeferredList([modules.stories.get_story_pub(idstory,0), modules.stories.get_stories_pub(0),modules.pages.get_pages_pub(0)])
		dl.addCallback(self._delayedChild,request)
		return DeferredResource(dl)
	def _delayedChild(self, res, request):
		if res[0][0] and res[0][1]!={} and res[1][0] and res[1][1]!=[]:
			s=Storyid(res)
			s.putChild('files', File("data/files/story/%s" % (res[0][1]['id']), "application/javascript"))
			return s
		return NoResource("No such resource.")
	def render_GET(self, request):
		return NoResource("No such resource.").render(request)
			

class Storyid(Resource):
	isLeaf = False
	def __init__(self, res):
		Resource.__init__(self)
		self.res = res
	def render_GET(self, request):
		ctx = {}
		ctx['story'] = self.res[0][1]
		ctx['story']['url']=request.getHeader('host')
		for i in range(len(self.res[1][1])):
			if self.res[1][1][i]['id']==self.res[0][1]['id']:
				del self.res[1][1][i]
				break
		#random.shuffle(res[1][1])
		ctx['stories'] = self.res[1][1]
		ctx['ratio'] = modules.constantes.conf['ratio']
		ctx['pages'] = self.res[2][1]
		ctx['footer'] = ''
		f="data/footer.html"
		if os.path.isfile(f):
			ctx['footer'] = unicode(open(f, "r").read(), 'utf-8')
		template = env.get_template("story.html")
		return template.render(ctx).encode('utf-8')

class Page(Resource):
	isLeaf = False
	def getChild(self, name, request):
		try:
			idpage=int(name)
		except:
			return self
		dl = defer.DeferredList([modules.pages.get_page_pub(idpage,0),modules.pages.get_pages_pub(0),modules.stories.get_story_last_pub(0)])
		dl.addCallback(self._delayedChild,request)
		return DeferredResource(dl)
	def _delayedChild(self, res, request):
		if res[0][0] and res[0][1]!={}:
			p=Pageid(res)
			return p
		return NoResource("No such resource.")
	def render_GET(self, request):
		return NoResource("No such resource.").render(request)
			

class Pageid(Resource):
	isLeaf = False
	def __init__(self, res):
		Resource.__init__(self)
		self.res = res
	def render_GET(self, request):
		ctx = {}
		ctx['brand'] = modules.constantes.conf['brand']
		ctx['page'] = self.res[0][1]
		ctx['pages'] = self.res[1][1]
		ctx['story'] = self.res[2][1]
		ctx['footer'] = ''
		f="data/footer.html"
		if os.path.isfile(f):
			ctx['footer'] = unicode(open(f, "r").read(), 'utf-8')
		template = env.get_template("page.html")
		return template.render(ctx).encode('utf-8')

class Public(object):
	def __init__(self):
		ctx = { }
		myroot = RootPage()
		myroot.putChild("story", Story())
		myroot.putChild("p", Page())
		myroot.putChild("s", selection.SelectionGroup())
		myroot.putChild('lib',File("public/lib", "application/javascript"))
		myroot.putChild('css',File("public/css", "application/javascript"))
		myroot.putChild('js',File("public/js", "application/javascript"))
		myroot.putChild('img',File("data/img", "application/javascript"))
		self.root=myroot			
