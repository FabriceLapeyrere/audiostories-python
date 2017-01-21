from twisted.internet import task
from twisted.internet import reactor
import os, json, sys, ws
import modules.stories
this = sys.modules[__name__]
this.conf={}

if not os.path.exists('data'):
	os.makedirs('data')
if not os.path.isfile('data/constantes.json'):
	f=open('data/constantes.json', "w+")
	f.write(json.dumps({
	'lang':'fr',
	'brand':'MyAudiostories',
	'ratio':1.5,
	'miniatures':{
		'mini':120,
		'petit':400,
		'normal':800,
		'hd':1600
		}
	}))
	f.close()
else:
	f=open('data/constantes.json', "r")
	this.conf=json.loads(f.read())
	f.close()

def commit():
	f=open('data/constantes.json', "w+")
	f.write(json.dumps(this.conf))
	f.close()
	
def addc(k,v,iduser):
	if iduser==1:
		try:
			value=json.loads(v)
		except:
			value=v
		if k not in this.conf:
			this.conf[k]=value
			this.commit()
			ws.maj(["*"],k,iduser)
def modc(k,v,iduser):
	if iduser==1:
		try:
			value=json.loads(v)
		except:
			value=v
		if k in this.conf:
			this.conf[k]=value
			this.commit()
			if k=='ratio' or k=='miniatures':
				task.deferLater(reactor, 1, modules.stories.check_data)
			ws.maj(["*"],k,iduser)
def delc(k,iduser):
	if iduser==1:
		if k in this.data:
			del this.conf[k]
			this.commit()
			ws.maj(["*"],k,iduser)

