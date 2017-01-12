import os, json, shutil
if not os.path.exists('data'):
	os.makedirs('data')
if not os.path.exists('data/img'):
	os.makedirs('data/img')
	for i in os.listdir('public/img'):
		srcname = os.path.join('public/img', i)
        	if os.path.isfile(srcname):
			shutil.copy(srcname,'data/img')

if not os.path.isfile('data/config.py'):
	conffile = open('data/config.py', "w+")
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
