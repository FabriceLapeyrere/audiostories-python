import os, json
if not os.path.isfile('data/config.py'):
	conffile = open('data/config.py', "w")
	conffile.write(json.dumps({
	'lang':'fr',
	'brand':'Audiostories',
	'ratio':1.5,
	'miniatures':{
		'mini':120,
		'petit':400,
		'normal':800,
		'hd':1600
	}
}))
	conffile.close()
f = open('data/config.py', "r")
conf=json.loads(f.read())
