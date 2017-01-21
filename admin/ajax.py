from twisted.web.server import NOT_DONE_YET
from twisted.web.resource import Resource
from ws.router import actions
import json, login
class Ajax(Resource):
	def __init__(self):
		Resource.__init__(self)
	def _delayedRender(self, res, request):
        	request.write(json.dumps(res))
        	request.finish()
	def render_POST(self, request):
		user=login.current_user(request)
		data = json.loads(request.content.getvalue())
		if data['action']=='logout':
			request.getSession().expire()
			return 'Logged out !'
		else:
			actions(data['action'],data['params'],user['uid']).addCallback(self._delayedRender,request)
			return NOT_DONE_YET
