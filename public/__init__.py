from zope.interface import implements
from twisted.internet import defer
from twisted.web.resource import Resource
from twisted.web.static import File
from twisted.web.server import NOT_DONE_YET
from jinja2 import Template, Environment, PackageLoader
from admin.modules.constantes import conf
from admin.modules.stories import Stories
from admin.modules.pages import Pages
from twisted.web import rewrite
from twisted.web.util import redirectTo
import random, json, os

env = Environment(loader=PackageLoader('public','templates'))
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

class RootPage(Resource):
	isLeaf=False
	def __init__(self):
		Resource.__init__(self)
	def getChild(self, name, request):
		if name == '':
			return self
		return Resource.getChild(self, name, request)
	def render_GET(self, request):
		S=Stories()
		P=Pages()
		dl = defer.DeferredList([S.get_stories_pub(0),P.get_pages_pub(0)])
		dl.addCallback(self._delayedRender,request)
		return NOT_DONE_YET
	def _delayedRender(self, res, request):
		ctx = {}
		ctx['stories'] = res[0][1]
		ctx['brand'] = conf['brand']
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
		if name == '':
			return self
		idstory=int(name)
		s=Storyid(idstory)
		s.putChild('files',File("data/files/story/%s" % (idstory), "application/javascript"))
		return s
	def render_GET(self, request):
		return redirectTo('/', request)
			

class Storyid(Resource):
	isLeaf = False
	def __init__(self, idstory):
		Resource.__init__(self)
		self.idstory = idstory
	def render_GET(self, request):
		idstory=self.idstory
		S=Stories()
		P=Pages()
		dl = defer.DeferredList([S.get_story_pub(idstory,0), S.get_stories_pub(0),P.get_pages_pub(0)])
		dl.addCallback(self._delayedRender,request)
		return NOT_DONE_YET
	def _delayedRender(self, res, request):
		if res[0][0] and res[0][1]!={} and res[1][0] and res[1][1]!=[]:
			ctx = {}
			ctx['story'] = res[0][1]
			for i in range(len(res[1][1])):
				if res[1][1][i]['id']==self.idstory:
					del res[1][1][i]
					break
			#random.shuffle(res[1][1])
			ctx['stories'] = res[1][1]
			ctx['ratio'] = conf['ratio']
			ctx['pages'] = res[2][1]
			ctx['footer'] = ''
			f="data/footer.html"
			if os.path.isfile(f):
				ctx['footer'] = unicode(open(f, "r").read(), 'utf-8')
			template = env.get_template("story.html")
			request.write(template.render(ctx).encode('utf-8'))
			request.finish()
		else:
			request.redirect('/')
			request.finish()
class Page(Resource):
	isLeaf = False
	def getChild(self, name, request):
		if name == '':
			return self
		idpage=int(name)
		s=Pageid(idpage)
		return s
	def render_GET(self, request):
		return redirectTo('/', request)
			

class Pageid(Resource):
	isLeaf = False
	def __init__(self, idpage):
		Resource.__init__(self)
		self.idpage = idpage
	def render_GET(self, request):
		idpage=self.idpage
		P=Pages()
		S=Stories()
		dl = defer.DeferredList([P.get_page_pub(idpage,0),P.get_pages_pub(0),S.get_story_last_pub(0)])
		dl.addCallback(self._delayedRender,request)
		return NOT_DONE_YET
	def _delayedRender(self, res, request):
		if res[0][0] and res[0][1]!={} and res[1][0] and res[1][1]!=[]:
			ctx = {}
			ctx['brand'] = conf['brand']
			ctx['page'] = res[0][1]
			ctx['pages'] = res[1][1]
			ctx['story'] = res[2][1]
			ctx['footer'] = ''
			f="data/footer.html"
			if os.path.isfile(f):
				ctx['footer'] = unicode(open(f, "r").read(), 'utf-8')
			template = env.get_template("page.html")
			request.write(template.render(ctx).encode('utf-8'))
			request.finish()
		else:
			request.redirect('/')
			request.finish()

class Public(object):
	def __init__(self):
		ctx = { }
		myroot = RootPage()
		myroot.putChild("story", Story())
		myroot.putChild("p", Page())
		myroot.putChild('lib',File("public/lib", "application/javascript"))
		myroot.putChild('css',File("public/css", "application/javascript"))
		myroot.putChild('js',File("public/js", "application/javascript"))
		myroot.putChild('img',File("data/img", "application/javascript"))
		myroot.putChild('files',File("data/files", "application/javascript"))
		self.root=myroot			
