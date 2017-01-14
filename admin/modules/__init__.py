from twisted.internet import defer
from user import User
from stories import Stories
from pages import Pages
import constantes

def actions(a,p,iduser):
	if a=="addAcl":
		u=user.User()
		return u.add_acl(p['type_ressource'],p['id_ressource'],p['type_acces'],p['id_acces'],p['level'],iduser)
	if a=="delAcl":
		u=user.User()
		return u.del_acl(p['type_ressource'],p['id_ressource'],p['type_acces'],p['id_acces'],p['level'],iduser)
	if a=="addUserGroup":
		u=user.User()
		return u.add_user_group(p['userid'],p['groupid'],iduser)
	if a=="delUserGroup":
		u=user.User()
		return u.del_user_group(p['userid'],p['groupid'],iduser)
	if a=="addGroup":
		u=user.User()
		return u.add_group(p['nom'],iduser)
	if a=="modGroup":
		u=user.User()
		return u.mod_group(p['id'],p['nom'],iduser)
	if a=="delGroup":
		u=user.User()
		return u.del_group(p['id'],iduser)
	if a=="addUser":
		u=user.User()
		return u.add_user(p['login'],p['name'],p['pwd'],iduser)
	if a=="modMoi":
		u=user.User()
		return u.mod_moi(p['id'],p['login'],p['name'],p.get('pwd',''),iduser)
	if a=="modUser":
		u=user.User()
		return u.mod_user(p['id'],p['login'],p['name'],p.get('pwd',''),p['role'],iduser)
	if a=="delUser":
		u=user.User()
		return u.del_user(p['id'],iduser)
	if a=="addPage":
		P=Pages()
		return P.add_page(p,iduser)
	if a=="modPage":
		P=Pages()
		return P.mod_page(p,iduser)
	if a=="delPage":
		P=Pages()
		return P.del_page(p,iduser)
	if a=="addStory":
		s=Stories()
		return s.add_story(p,iduser)
	if a=="modStory":
		s=Stories()
		return s.mod_story(p,iduser)
	if a=="modStatut":
		s=Stories()
		return s.mod_statut(p,iduser)
	if a=="delStory":
		s=Stories()
		return s.del_story(p,iduser)
	if a=="delFile":
		s=Stories()
		return defer.maybeDeferred(lambda: s.del_file(p,iduser))
	if a=="addConstante":
		return defer.maybeDeferred(lambda: constantes.addc(p['k'],p['v'],iduser))
	if a=="delConstante":
		return defer.maybeDeferred(lambda: constantes.delc(p['k'],iduser))
	if a=="modConstante":
		return defer.maybeDeferred(lambda: constantes.modc(p['k'],p['v'],iduser))
	return defer.maybeDeferred(lambda: 'no action match')
def gets(tab,res,iduser):
	if tab[0]=="group":
		res=User().get_group(tab[1],iduser)
	if tab[0]=="groups":
		res=User().get_groups(iduser)
	if tab[0]=="user":
		res=User().get_user(tab[1],iduser)
	if tab[0]=="users":
		res=User().get_users(iduser)
	if tab[0]=="usersall":
		res=User().get_users_all(iduser)
	if tab[0]=="stories":
		res=Stories().get_stories(iduser)
	if tab[0]=="story":
		res=Stories().get_story(tab[1],iduser)
	if tab[0]=="pages":
		res=Pages().get_pages(iduser)
	if tab[0]=="page":
		res=Pages().get_page(tab[1],iduser)
	if tab[0]=="constantes":
		res=constantes.data.copy()
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
