from twisted.internet import defer
import modules.stories
import modules.pages
import modules.user
import modules.constantes

def actions(a,p,iduser):
	if a=="addAcl":
		return modules.user.add_acl(p['type_ressource'],p['id_ressource'],p['type_acces'],p['id_acces'],p['level'],iduser)
	if a=="delAcl":
		return modules.user.del_acl(p['type_ressource'],p['id_ressource'],p['type_acces'],p['id_acces'],p['level'],iduser)
	if a=="addUserGroup":
		return modules.user.add_user_group(p['userid'],p['groupid'],iduser)
	if a=="delUserGroup":
		return modules.user.del_user_group(p['userid'],p['groupid'],iduser)
	if a=="addGroup":
		return modules.user.add_group(p['nom'],iduser)
	if a=="modGroup":
		return modules.user.mod_group(p['id'],p['nom'],iduser)
	if a=="delGroup":
		return modules.user.del_group(p['id'],iduser)
	if a=="addUser":
		return modules.user.add_user(p['login'],p['name'],p['pwd'],iduser)
	if a=="modMoi":
		return modules.user.mod_moi(p['id'],p['login'],p['name'],modules.pages.get('pwd',''),iduser)
	if a=="modUser":
		return modules.user.mod_user(p['id'],p['login'],p['name'],modules.pages.get('pwd',''),p['role'],iduser)
	if a=="delUser":
		return modules.user.del_user(p['id'],iduser)
	if a=="addPage":
		return modules.pages.add_page(p,iduser)
	if a=="modPage":
		return modules.pages.mod_page(p,iduser)
	if a=="delPage":
		return modules.pages.del_page(p,iduser)
	if a=="addStory":
		return modules.stories.add_story(p,iduser)
	if a=="modStory":
		return modules.stories.mod_story(p,iduser)
	if a=="modStatut":
		return modules.stories.mod_statut(p,iduser)
	if a=="delStory":
		return modules.stories.del_story(p,iduser)
	if a=="delFile":
		return defer.maybeDeferred(lambda: modules.stories.del_file(p,iduser))
	if a=="addConstante":
		return defer.maybeDeferred(lambda: modules.constantes.addc(p['k'],p['v'],iduser))
	if a=="delConstante":
		return defer.maybeDeferred(lambda: modules.constantes.delc(p['k'],iduser))
	if a=="modConstante":
		return defer.maybeDeferred(lambda: modules.constantes.modc(p['k'],p['v'],iduser))
	return defer.maybeDeferred(lambda: 'no action match')
def gets(tab,res,iduser):
	if tab[0]=="group":
		res=modules.user.get_group(tab[1],iduser)
	if tab[0]=="groups":
		res=modules.user.get_groups(iduser)
	if tab[0]=="user":
		res=modules.user.get_user(tab[1],iduser)
	if tab[0]=="users":
		res=modules.user.get_users(iduser)
	if tab[0]=="usersall":
		res=modules.user.get_users_all(iduser)
	if tab[0]=="stories":
		res=modules.stories.get_stories(iduser)
	if tab[0]=="story":
		res=modules.stories.get_story(tab[1],iduser)
	if tab[0]=="pages":
		res=modules.pages.get_pages(iduser)
	if tab[0]=="page":
		res=modules.pages.get_page(tab[1],iduser)
	if tab[0]=="constantes":
		res=modules.constantes.conf.copy()
	return res
def deps(tab,res):
	if tab[0]=="group":
		res.append('groups')
	if tab[0]=="story":
		res.append('stories')
	if tab[0]=="page":
		res.append('pages')
	if tab[0]=="user":
		res.append('users')
		res.append('usersall')
	if tab[0]=="users":
		res.append('usersall')
	return res

def context_verrou(ctype):
	tab=ctype.split('/')
	print("context verrou %s" % ctype)
	if tab[0]=="user":
		return 'users'
	if tab[0]=="group":
		return 'groups'
	if tab[0]=="page":
		return 'pages'
	if "story_" in tab[0]:
		return 'story/%s' % tab[1]
	return ctype;

