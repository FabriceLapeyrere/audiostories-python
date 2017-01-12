from twisted.internet import task, reactor
from twisted.web.server import NOT_DONE_YET
from modules.stories import Stories
from modules.user import User
from twisted.web import iweb
from twisted.web.resource import Resource
import cgi, glob, re, unicodedata, os, login

class Upload(Resource):
	def __init__(self):
		Resource.__init__(self)
	def strip_accents(self,text):
		"""
		Strip accents from input String.

		:param text: The input string.
		:type text: String.

		:returns: The processed String.
		:rtype: String.
		"""
		try:
			text = unicode(text, 'utf-8')
		except NameError: # unicode is a default on python 3 
			pass
		text = unicodedata.normalize('NFD', text)
		text = text.encode('ascii', 'ignore')
		text = text.decode("utf-8")
		return str(text)

	def filter(self,text):
		"""
		Convert input text to id.

		:param text: The input string.
		:type text: String.

		:returns: The processed String.
		:rtype: String.
		"""
		text = self.strip_accents(text.lower())
		text = re.sub('[ ]+', '_', text)
		text = re.sub('[^0-9a-zA-Z_-]', '', text)
		return text
	def do_write(self,res,idstory,typedoc,user,f,request):
		if res==1:
			if typedoc=='story':
				filename,ext=os.path.splitext(f.filename)
				if ext in ['.png','.PNG','.jpg','.JPG','.jpeg','.JPEG']:
					uploadDir = "data/files/story/%s" % (idstory)
					new_file_name="%s%s" % (self.filter(filename),ext)
					uploadPath = "%s/%s" % (uploadDir,new_file_name)
					if not os.path.isdir(uploadDir):
						os.makedirs(uploadDir)
					i=1
					path=uploadPath
					while os.path.isfile(path):
						new_file_name="%s-%s%s" % (self.filter(filename),i,ext)
						path="%s/%s" % (uploadDir,new_file_name)
						i+=1
					fp =open(path,'wb')
					fp.write(f.value)
					fp.close()
					s=Stories()
					task.deferLater(reactor, 1, s.check_miniatures, idstory).addCallback(lambda x:s.touch_story(idstory,user['uid']))
					request.write('ok')
					request.finish()
			if typedoc=='faceA' or typedoc=='faceB':
				filename,ext=os.path.splitext(f.filename)
				if ext in ['.wav','.WAV']:
					for fold in glob.iglob("data/files/story/%s/%s/*" % (idstory,typedoc)):
						os.remove(fold)
					uploadDir = "data/files/story/%s/%s" % (idstory,typedoc)
					new_file_name="%s%s" % (self.filter(filename),ext)
					uploadPath = "%s/%s" % (uploadDir,new_file_name)
					if not os.path.isdir(uploadDir):
						os.makedirs(uploadDir)
					fp =open(uploadPath,'wb')
					fp.write(f.value)
					fp.close()
					s=Stories()
					task.deferLater(reactor, 1, s.check_waveform, idstory).addCallback(lambda x:s.touch_story(idstory,user['uid']))
					request.write('ok')
					request.finish()	
		else:
			request.write('ko')
			request.finish()
		
	def render_POST(self, request):
		user=login.current_user(request)
		if not user['login']:
			return 'ko'
		headers=request.getAllHeaders()
		form = cgi.FieldStorage(
			fp = request.content,
			headers = headers,
			environ = {'REQUEST_METHOD':'POST', 'CONTENT_TYPE': headers['content-type']}
		)
		idstory = form['id'].value
		typedoc = form['type'].value
		f=form[ 'file' ]
		u=User()
		u.is_allowed('stories',idstory,1,user['uid']).addCallback(self.do_write,idstory,typedoc,user,f,request)
		return NOT_DONE_YET
