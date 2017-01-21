import db, ws, sys, os, json, glob, time, Image, modules
from twisted.internet import task
from twisted.internet import reactor
import numpy as np
import soundfile as sf
import re

this = sys.modules[__name__]

def get_story(storyid,iduser):
	return db.connexion.runQuery("SELECT (SELECT count(*)+1 FROM stories WHERE date<t1.date AND statut=1) as num, '[' || Group_Concat(DISTINCT t2.id_acces) ||']' as groups, t1.id as id, t1.nom as nom, t1.pitch as pitch, t1.photos as photos, t1.couleur as couleur, t1.sons as sons, t1.desc as desc, t1.createdby as createdby, t1.creationdate as creationdate, t1.date as date, t1.modificationdate as modificationdate, t1.modifiedby as modifiedby, t1.statut as statut FROM stories as t1 left outer join acl as t2 on t2.id_ressource=t1.id AND t2.type_ressource='stories' AND t2.type_acces='group' where t1.id=? AND (?=1 OR createdby=? OR t1.id IN (SELECT id_ressource from acl where type_ressource='stories' AND type_acces='group' AND id_acces IN (select id_group from user_group where id_user=?))) group by t1.id", (storyid,iduser,iduser,iduser)).addCallback(this.build_story,iduser)
def get_story_pub(storyid,iduser):
	return db.connexion.runQuery("SELECT (SELECT count(*)+1 FROM stories WHERE date<t1.date AND statut=1) as num, * FROM stories as t1  WHERE t1.id=? and t1.statut=1", (storyid,)).addCallback(this.build_story,iduser)
def get_story_last_pub(iduser):
	return db.connexion.runQuery("SELECT (SELECT count(*)+1 FROM stories WHERE date<t1.date AND statut=1) as num, * FROM stories as t1  WHERE t1.statut=1 and t1.date = (SELECT MAX(date) from stories where statut=1)").addCallback(this.build_story,iduser)
def build_story(dbentries,iduser):
	if len(dbentries)==1:
		row=dbentries[0]
		row['files']=[]
		row['miniatures']={}
		for f in glob.iglob("data/files/story/%s/*" % row['id']):
			if os.path.isfile(f):
				basename=os.path.basename(f)
				filename,ext=os.path.splitext(basename)
				if ext in ['.png','.PNG','.jpg','.JPG','.jpeg','.JPEG']:
					row['files'].append({'filename':basename,'date':os.path.getmtime(f)})
					row['miniatures'][basename]={}
					for nom,w in modules.constantes.conf['miniatures'].items():
						h=int(w/modules.constantes.conf['ratio'])
						if os.path.isfile("data/files/story/%s/min/%s_%s_%s.jpg" % (row['id'],filename,w,h)):
							row['miniatures'][basename][nom]="min/%s_%s_%s.jpg" % (filename,w,h)	
		row['sons']=json.loads(row['sons'])
		if 'A' not in row['sons']:
			row['sons']['A']={}
		if 'B' not in row['sons']:
			row['sons']['B']={}
		if 'file' not in row['sons']['A']:
			row['sons']['A']['file']={}
		if 'file' not in row['sons']['B']:
			row['sons']['B']['file']={}
		if 'subs' not in row['sons']['A']:
			row['sons']['A']['subs']={}
		if 'subs' not in row['sons']['B']:
			row['sons']['B']['subs']={}
		if 'fr' not in row['sons']['A']['subs']:
			row['sons']['A']['subs']['fr']=[]
		if 'fr' not in row['sons']['B']['subs']:
			row['sons']['B']['subs']['fr']=[]
		for lang in row['sons']['A']['subs']:
			for x in range(len(row['sons']['A']['subs'][lang])):	
				row['sons']['A']['subs'][lang][x]['verrou']=ws.get_verrou('story_A_subs_%s_%s/%s' % (lang,row['sons']['A']['subs'][lang][x]['uuid'],row['id']))
		for lang in row['sons']['B']['subs']:
			for x in range(len(row['sons']['B']['subs'][lang])):	
				row['sons']['B']['subs'][lang][x]['verrou']=ws.get_verrou('story_B_subs_%s_%s/%s' % (lang,row['sons']['B']['subs'][lang][x]['uuid'],row['id']))
		for f in glob.iglob("data/files/story/%s/faceA/*" % row['id']):
			if os.path.isfile(f):
				basename=os.path.basename(f)
				filename,ext=os.path.splitext(basename)
				if ext in ['.mp3','.wav','.WAV','.MP3']:
					row['sons']['A']['file']['path']=f
					row['sons']['A']['file']['filename']=basename
					row['sons']['A']['file']['date']=os.path.getmtime(f)
					d = json.loads(open("%s.json" % f, "r").read())
					row['sons']['A']['peaks']=d['peaks']
					row['sons']['A']['infos']=d['infos']
		for f in glob.iglob("data/files/story/%s/faceB/*" % row['id']):
			if os.path.isfile(f):
				basename=os.path.basename(f)
				filename,ext=os.path.splitext(basename)
				if ext in ['.mp3','.wav','.WAV','.MP3']:
					row['sons']['B']['file']['path']=f
					row['sons']['B']['file']['filename']=basename
					row['sons']['B']['file']['date']=os.path.getmtime(f)
					d = json.loads(open("%s.json" % f, "r").read())
					row['sons']['B']['peaks']=d['peaks']
					row['sons']['B']['infos']=d['infos']
		row['statut']=True if row['statut'] else False
		row['date']=0+row['date']
		row['photos']=json.loads(row['photos'])
		row['couleur']=json.loads(row['couleur'])
		row['gradient']="gradient/%s_%s_%s_%s.jpg" % (row['couleur'][0][1:],row['couleur'][1][1:],row['couleur'][2][1:],row['couleur'][3][1:])
		row['infos']={}
		d=row['desc']
		if d:
			auteurs = re.findall("<p>@(.*)</p>", d)
			for a in auteurs:
				d=d.replace("<p>@%s</p>" % (a),"")
			liens = re.findall("<p>#(.*)</p>", d)
			for l in liens:
				d=d.replace("<p>#%s</p>" % (l),"")
			row['infos']['auteurs']=', '.join(auteurs)
			row['infos']['liens']='<br />'.join(liens)
			row['infos']['texte']=d
		else:
			row['infos']['auteurs']=''
			row['infos']['liens']=''
			row['infos']['texte']=''
		try:
			row['groups']=json.loads(row['groups'])
		except:
			row['groups']=[]
		row['verrou_nom']=ws.get_verrou('story_nom/%s' % (row['id']))
		row['verrou_pitch']=ws.get_verrou('story_pitch/%s' % (row['id']))
		row['verrou_faceA']=ws.get_verrou('story_faceA/%s' % (row['id']))
		row['verrou_faceB']=ws.get_verrou('story_faceB/%s' % (row['id']))
		row['verrou_date']=ws.get_verrou('story_date/%s' % (row['id']))
		row['verrou_desc']=ws.get_verrou('story_desc/%s' % (row['id']))
		row['verrou_couleur']=ws.get_verrou('story_couleur/%s' % (row['id']))
		return row
	return {}
def build_header(dbentries,iduser):
	row=dbentries[0]
	row['photos']=json.loads(row['photos'])
	row['une']={}
	for nom,w in modules.constantes.conf['miniatures'].items():
		basename=os.path.basename(row['photos']['une'])
		filename,ext=os.path.splitext(basename)
		h=int(w/modules.constantes.conf['ratio'])
		row['une'][nom]="min/%s_%s_%s.jpg" % (filename,w,h)	
	del row['photos']
	try:
		row['groups']=json.loads(row['groups'])
	except:
		row['groups']=[]
	row['statut']=True if row['statut'] else False
	row['date']=0+row['date']
	row['couleur']=json.loads(row['couleur'])
	row['gradient']="gradient/%s_%s_%s_%s.jpg" % (row['couleur'][0][1:],row['couleur'][1][1:],row['couleur'][2][1:],row['couleur'][3][1:])
	return row
def get_stories(iduser):
	return db.connexion.runQuery("SELECT (SELECT count(*)+1 FROM stories WHERE date<t1.date AND statut=1) as num, '[' || Group_Concat(DISTINCT t2.id_acces) ||']' as groups, t1.id as id, t1.nom as nom, t1.pitch as pitch, t1.photos as photos, t1.couleur as couleur, t1.createdby as createdby, t1.creationdate as creationdate, t1.date as date, t1.modificationdate as modificationdate, t1.modifiedby as modifiedby, t1.statut as statut FROM stories as t1 left outer join acl as t2 on t2.id_ressource=t1.id AND t2.type_ressource='stories' AND t2.type_acces='group' WHERE ?=1 OR t1.createdby=? OR t1.id IN (SELECT id_ressource from acl where type_ressource='stories' AND type_acces='group' AND id_acces IN (select id_group from user_group where id_user=?)) group by t1.id ORDER BY t1.id ASC", (iduser,iduser,iduser)).addCallback(this.build_stories,iduser)
def get_stories_pub(iduser):
	return db.connexion.runQuery("SELECT (SELECT count(*)+1 FROM stories WHERE date<t1.date AND statut=1) as num, id, nom, pitch, photos, couleur, createdby, creationdate, date, modificationdate, modifiedby, statut FROM stories as t1 WHERE t1.statut=1 ORDER BY num desc").addCallback(this.build_stories,iduser)
def build_stories(dbentries,iduser):
	stories=[]
	for row in dbentries:
		stories.append(this.build_header([row],iduser))
	return stories
def do_touch_story(txn,idstory,iduser):
	now=int(time.time()*1000.0)
	txn.execute('UPDATE stories SET modificationdate=?, modifiedby=? WHERE id=?', (now, iduser, idstory))
	return idstory
def touch_story(idstory,iduser):
	return db.connexion.runInteraction(this.do_touch_story, idstory, iduser).addCallback(lambda idstory: ws.maj(["story/%s" % idstory],idstory,iduser))
def del_file(params,iduser):
	idstory=params['id']
	f=params['file']
	os.remove("data/files/story/%s/%s" % (idstory,f['filename']));
	for minf in glob.iglob("data/files/story/%s/min/%s*" % (idstory,f['filename'])):
		os.remove(minf)
	this.touch_story(idstory,iduser);
def do_mod_story(txn,params,iduser):
	now=int(time.time()*1000.0)
	idstory=params.get('id','')
	nom=params.get('nom','')
	desc=params.get('desc','')
	pitch=params.get('pitch','')
	couleur=params.get('couleur',['#ffffff','#ffffff','#ffffff','#ffffff'])
	sons=params.get('sons',[])
	photos=params.get('photos',[])
	date=params.get('date',0)
	txn.execute('UPDATE stories SET nom=?, desc=?, pitch=?, couleur=?, sons=?, photos=?, date=?, modificationdate=?, modifiedby=? WHERE id=?',(nom,desc,pitch,json.dumps(couleur),json.dumps(sons),json.dumps(photos),date, now, iduser,idstory))
	task.deferLater(reactor, 1, this.check_gradient, idstory, couleur).addCallback(lambda x:this.touch_story(idstory,iduser))
	return idstory
def mod_story(params,iduser):
	return db.connexion.runInteraction(this.do_mod_story, params, iduser).addCallback(lambda idstory: ws.maj(["story/%s" % idstory],idstory,iduser))
def do_mod_statut(txn,params,iduser):
	now=int(time.time()*1000.0)
	idstory=params.get('id','')
	statut=params.get('statut','')
	txn.execute('UPDATE stories SET statut=?, modificationdate=?, modifiedby=? WHERE id=? AND ? in (SELECT id FROM users WHERE role=2)',(statut, now, iduser,idstory,iduser))
	return idstory
def mod_statut(params,iduser):
	return db.connexion.runInteraction(this.do_mod_statut, params, iduser).addCallback(lambda idstory: ws.maj(["story/%s" % idstory],idstory,iduser))
def do_del_story(txn,params,iduser):
	idstory=params['story']['id']
	story=params['story']
	now=int(time.time()*1000.0)
	txn.execute('INSERT INTO trash (id_item, type, json, date , by) VALUES (?,?,?,?,?) ',(idstory,'story',json.dumps(story),now,iduser))
	txn.execute('DELETE FROM stories WHERE id=? ', (idstory,))
	return idstory
def del_story(params,iduser):
	return db.connexion.runInteraction(this.do_del_story, params, iduser).addCallback(lambda idstory: ws.maj(["story/%s" % idstory],idstory,iduser))
def do_add_story(txn,params,iduser):
	nom=params['story']['nom']
	now=int(time.time()*1000.0)
	txn.execute('INSERT INTO stories (nom, desc, pitch, couleur, sons, photos, statut, date,  creationdate, createdby, modificationdate, modifiedby) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',(nom, '', '', json.dumps(['#FFFFFF','#FF0000','#00FF00','#0000FF']), '{}', json.dumps({'une':'','paires':[]}), 0, now, now, iduser, now, iduser))
	return txn.lastrowid
def add_story(params,iduser):
	return db.connexion.runInteraction(this.do_add_story, params, iduser).addCallback(lambda idstory: ws.maj(["story/%s" % idstory],idstory,iduser))
def do_check_data(dbentries):
	for row in dbentries:
		this.check_miniatures(row['id'])
		this.check_waveform(row['id'])
		couleur=json.loads(row['couleur'])
		if len(couleur)!=4:
			couleur=['#ffffff','#ffffff','#ffffff','#ffffff']
		this.check_gradient(row['id'],couleur)
	print('Data checked !!')
def check_data():
	return db.connexion.runQuery("SELECT * FROM stories").addCallback(this.do_check_data)
def check_miniatures(idstory):
	doneSomething=False
	for f in glob.iglob("data/files/story/%s/*" % idstory):
		if os.path.isfile(f):
			dirname=os.path.dirname(f)
			basename=os.path.basename(f)
			filename,ext=os.path.splitext(basename)
			if ext in ['.png','.PNG','.jpg','.JPG','.jpeg','.JPEG']:
				for nom,w in modules.constantes.conf['miniatures'].items():
					h=int(w/modules.constantes.conf['ratio'])
					if this.do_miniature(w,h,f):
						doneSomething=True
	if doneSomething:
		ws.maj(['story/%s' % idstory],idstory,1)
def check_waveform(idstory):
	for f in glob.iglob("data/files/story/%s/face*/*" % idstory):
		if os.path.isfile(f):
			basename=os.path.basename(f)
			filename,ext=os.path.splitext(basename)
			if ext in ['.mp3','.wav','.WAV','.MP3']:
				jsonfilename="%s.json" % f
				if not os.path.isfile(jsonfilename):
					try:
						infos=sf.info(f)
						rms = [np.max(block)*0.9 for block in sf.blocks(f, blocksize=50000)]
						d={'infos':{'channels':infos.channels, 'samplerate':infos.samplerate, 'duration':infos.duration, 'format':infos.format, 'subtype':infos.subtype}, 'peaks':rms}
						jsonfile = open(jsonfilename, "w")
						jsonfile.write(json.dumps(d))
						print('waveform %s done !' % f)
					except:
						os.remove(f)
	return "ok"
def check_gradient(idstory ,couleurs):
	dest="data/files/story/%s/gradient/%s_%s_%s_%s.jpg" % (idstory,couleurs[0][1:],couleurs[1][1:],couleurs[2][1:],couleurs[3][1:])
	graddir="data/files/story/%s/gradient/" % idstory
	if not os.path.isdir(graddir):
		os.makedirs(graddir)
	if not os.path.isfile(dest):
		this.gradient(1000, 1000, couleurs, dest, idstory)
def gradient(w, h, hc, dest, idstory):
	c=[this.hex2rgb(hcolor[1:]) for hcolor in hc ]
	pixels=[]
	for x in range(w):
		for y in range(h):
			xf=float(x)
			yf=float(y)
			wf=float(w)
			hf=float(h)
			rgb=[ int(c[0][i]*((wf-xf)*(hf-yf)/(wf*hf)) + c[1][i]*(xf*(hf-yf)/(wf*hf)) + c[2][i]*((wf-xf)*yf/(wf*hf)) + c[3][i]*(xf*yf/(wf*hf))) for i in range(3)]
			pixels.append(tuple(rgb))
	img = Image.new("RGB", (w,h))
	img.putdata(pixels)
	for f in glob.iglob("data/files/story/%s/gradient/*.jpg" % idstory):
		os.remove(f)
	img.save(dest, "JPEG", quality=90)
	print('gradient done !')
def hex2rgb(h):
	try:
		int(h, 16)
		if len(h)==6:
			return [int(h[2*i:2*i+2], 16) for i in range(3)]
		else:
			return [255,255,255]
	except:
		return [255,255,255]
def do_miniature(w,h,f):
	dirname=os.path.dirname(f)
	basename=os.path.basename(f)
	filename,ext=os.path.splitext(basename)
	mindir="%s/min" % dirname
	if not os.path.isdir(mindir):
		os.makedirs(mindir)
	dest="%s/%s_%s_%s.jpg" % (mindir,filename,w,h)
	if not os.path.isfile(dest):
		img=Image.open(f)
		largeur, hauteur = img.size
		w=float(w)
		h=float(h)
		largeur=float(largeur)
		hauteur=float(hauteur)
		if w/h>largeur/hauteur:
			width=w
			r=width/largeur
			height=r*hauteur
			haut=int((height-h)/2)
			bas=int(haut+h)
			crop=(0,haut,int(width),bas)
		else:
			height=h
			r=height/hauteur
			width=r*largeur
			gauche=int((width-w)/2)
			droite=int(gauche+w)
			crop=(gauche,0,droite,int(h))
		resized=img.resize((int(r*largeur), int(r*hauteur)))
		cropped=resized.crop(crop)
		cropped.save(dest, "JPEG", quality=90)
		print('miniature %s done !' % dest)
		return True
	return False
