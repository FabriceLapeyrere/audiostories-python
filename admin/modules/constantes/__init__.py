import os, json, sys, admin
this = sys.modules[__name__]
this.data={}
if not os.path.exists('data'):
	os.makedirs('data')
if not os.path.isfile('data/constantes.json'):
	f=open('data/constantes.json', "w+")
	f.write(json.dumps({}))
	f.close()
else:
	f=open('data/constantes.json', "r")
	this.data=json.loads(f.read())
	f.close()

def commit():
	f=open('data/constantes.json', "w+")
	f.write(json.dumps(this.data))
	f.close()
	
def addc(k,v,iduser):
	if iduser==1:
		if k not in this.data:
			this.data[k]=v
			this.commit()
			admin.wsrouter.maj(["constantes"],k,iduser)
def modc(k,v,iduser):
	if iduser==1:
		if k in this.data:
			this.data[k]=v
			this.commit()
			admin.wsrouter.maj(["constantes"],k,iduser)
def delc(k,iduser):
	if iduser==1:
		if k in this.data:
			del this.data[k]
			this.commit()
			admin.wsrouter.maj(["constantes"],k,iduser)

