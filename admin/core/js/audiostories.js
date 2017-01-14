/**
 *
 * @license		GPL 3 (http://www.gnu.org/licenses/gpl.html)
 * @author		 Fabrice Lapeyrere <fabrice.lapeyrere@surlefil.org>
 */
'use strict';
moment.lang('fr');
var  debounce = function(fn, delay) {
  var timer = null;
  return function () {
    var context = this, args = arguments;
    clearTimeout(timer);
    timer = setTimeout(function () {
      fn.apply(context, args);
    }, delay);
  };
}
var rgb2hex=function(rgb){
 rgb = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
 return "#" +
	("0" + parseInt(rgb[1],10).toString(16)).slice(-2) +
	("0" + parseInt(rgb[2],10).toString(16)).slice(-2) +
	("0" + parseInt(rgb[3],10).toString(16)).slice(-2);
}
var app= angular.module('audiostories', ['ngRoute','monospaced.mousewheel','ngDragDrop','ui.bootstrap', 'toggle-switch', 'angularFileUpload','ngSanitize','cfp.hotkeys','ngCkeditor','myws']);

app.config(['$routeProvider', function($routeProvider) {
	//stories
	$routeProvider.when('/stories', {templateUrl: 'stories_partials/stories.html', controller: 'storiesCtl'});
	$routeProvider.when('/modstory/:id', {templateUrl: 'stories_partials/modstory.html', controller: 'modstoryCtl'});
	//pages
	$routeProvider.when('/pages', {templateUrl: 'pages_partials/pages.html', controller: 'pagesCtl'});
	$routeProvider.when('/modpage/:id', {templateUrl: 'pages_partials/modpage.html', controller: 'modpageCtl'});
	//admin
	$routeProvider.when('/moduser/:id', {templateUrl: 'user_partials/moduser.html', controller: 'modUserCtl'});
	$routeProvider.when('/adduser', {templateUrl: 'user_partials/adduser.html', controller: 'addUserCtl'});
	$routeProvider.when('/modgroup/:id', {templateUrl: 'user_partials/modgroup.html', controller: 'modGroupCtl'});
	$routeProvider.when('/addgroup', {templateUrl: 'user_partials/addgroup.html', controller: 'addGroupCtl'});
	$routeProvider.when('/modconstante/:id', {templateUrl: 'constantes_partials/modconstante.html', controller: 'modConstanteCtl'});
	$routeProvider.when('/addconstante', {templateUrl: 'constantes_partials/addconstante.html', controller: 'addConstanteCtl'});
	$routeProvider.when('/admin', {templateUrl: 'user_partials/admin.html', controller: 'adminCtl'});
	$routeProvider.when('/moi', {templateUrl: 'user_partials/me.html', controller: 'moiCtl'});
	$routeProvider.otherwise({redirectTo: '/stories'});
}]);
app.config(['$locationProvider', function($locationProvider) {
	$locationProvider.html5Mode(true);
}]);
app.config( [
		'$compileProvider',
		function( $compileProvider )
		{	 
				$compileProvider.imgSrcSanitizationWhitelist(/^\s*(https?|ftp|data):/);
		}
]);
app.controller('mainCtl', ['$scope', '$http', '$location', '$interval', '$modal', '$q', '$window', '$sce', 'Link', 'Data', function ($scope, $http, $location, $interval, $modal, $q, $window, $sce, Link, Data) {
	$scope.uploaders={};
	$scope.srt={A:[],B:[]};
	$scope.Data=Data;
	$scope.editorOptions = {
		language: 'fr'
	};
	$scope.params='test';
	$scope.done=false;
	$scope.brand='';
	$scope.conf={};
	$scope.story=[];
	$scope.tags=[];
	$scope.stories=[];
	$scope.pages=[];
	$scope.majTime=0;
	$scope.logged={id:0};
	$scope.pageCourante={};
	$scope.pageCourante.stories=1;
	$scope.pageCourante.news=1;
	$scope.afterLogin='';
	$scope.studio={};
	$scope.studio.files=[];
	$scope.studio.gauche={};
	$scope.studio.droit={};
	$scope.show={};
	$scope.path=function(){return $location.path();}
	$scope.trust=function(html){
		return $sce.trustAsHtml(html);
	}
	$scope.logout=function(){
		$window.location="logout";
	};
	$scope.calendar=function(t){
		var date=moment(parseInt(t));;
		return date.calendar();
	}
	$scope.horaire=function(t){
		var date=moment(parseInt(t) * 1000);;
		return date.format('HH[h]mm:ss');
	}
	$scope.byId=function(a,id){
		var res=false;
		angular.forEach(a,function(e){
			if(e.id==id) {
				res=e;
				return;
			}
		});
		return res;
	};
	$scope.isChild = function( parent ) {
		return function( item ) {
		return item.id_parent == parent.id;
		};
	};
	$scope.hasChild=function(tag){
		var res=false;
		angular.forEach($scope.tags, function(t){
			if (t.id_parent==tag.id){
				res=true;
			}
		});
		return res;
	
	}
	$scope.isEqual=function(a,b){
		if (a && b) {
			var ac=angular.copy(a);
			var bc=angular.copy(b);
			if (ac.date && bc.date) {
				ac.date=new Date(ac.date).getTime();
				bc.date=new Date(bc.date).getTime();
			}
			if (ac.desc=='<p></p>') ac.html=''; 
			if (ac.desc===null) ac.desc='';
			if (bc.desc=='<p></p>') bc.html=''; 
			if (bc.desc===null) bc.desc='';
			if (ac.html=='<p></p>') ac.html=''; 
			if (ac.html===null) ac.html='';
			if (bc.html=='<p></p>') bc.html=''; 
			if (bc.html===null) bc.html='';
			return JSON.stringify(ac, null, 4)==JSON.stringify(bc, null, 4);
		}
		return true;
	};
	$scope.min=function(a,b){
		return Math.min(a,b);
	};
	$scope.index=function(k,a,v){
		var i=-1;
		angular.forEach(a,function(e){
			if(e[k]==v) {
				i=a.indexOf(e);
				return;
			}
		});
		return i;
	};
	$scope.addStoryMod=function(){
		$scope.addStory={};
		var modal = $modal.open({
			templateUrl: 'stories_partials/addstorymod.html',
			controller: 'addStoryModCtl',
			resolve:{
				story: function () {
					return $scope.addStory;
				}
			}
		});

		modal.result.then(function (story) {
			var data={
				action:'addStory',
				params:{story:story}
			};
			Link.ajax(data,function(r){
				$location.path('/modstory/'+ r.data);
			});
		});
	};
	$scope.addPageMod=function(){
		$scope.addPage={};
		var modal = $modal.open({
			templateUrl: 'pages_partials/addpagemod.html',
			controller: 'addPageModCtl',
			resolve:{
				page: function () {
					return $scope.addPage;
				}
			}
		});

		modal.result.then(function (page) {
			var data={
				action:'addPage',
				params:{page:page}
			};
			Link.ajax(data,function(r){
				$location.path('/modpage/'+ r.data);
			});
		});
	};
	$scope.stripAccents=function(str){
		if (str){
			return removeDiacritics(str);
		}
	};
	$scope.descTagRec=function(tag){
		var h=[tag];
		if (tag.id_parent!=0){
			angular.forEach($scope.descTagRec($scope.byId($scope.tags,tag.id_parent)), function(t){
				h.push(t);
			});
		}
		return h;
	};
	$scope.descTag=function(tag){
		var h=$scope.descTagRec(tag);
		return h.reverse();
	};
	$scope.itemsParPage=10;
	$scope.maxSize = 5;
	$scope.parNomTag = function(tags) {
		tags.sort(function(a,b) {
			var tagA=$scope.byId($scope.tags,a);
			var tagB=$scope.byId($scope.tags,b);
			return tagA.nom.localeCompare(tagB.nom);
		});
		return tags;
	};
	$scope.arrondi= function(f){return Math.floor(f);};
	$scope.pristine=function(key){
		return $scope.isEqual(Data.modele[key],Data.modeleSrv[key]);       
	};
	$scope.dirty=function(key){
		return !$scope.pristine(key);       
	};
	$scope.trust=function(html){
		return $sce.trustAsHtml(html);
	}
	
}]);
app.controller('accueilCtl', ['$scope', '$http', '$location', function ($scope, $http, $location) {	
	$scope.done=true;
}]);

//stories
app.controller('storiesCtl', ['$scope', '$http', '$location', '$modal', 'Link', 'Data', function ($scope, $http, $location, $modal, Link, Data) {
	$scope.Data=Data;
	Link.context([{type:'stories', params:{}}]);
	$scope.delStory=function(story){
		var data={
			action:'delStory',
			params:{story:story}
		};
		Link.ajax(data,function(){});		
	};
}]);

//pages
app.controller('pagesCtl', ['$scope', '$http', '$location', '$modal', 'Link', 'Data', function ($scope, $http, $location, $modal, Link, Data) {
	$scope.Data=Data;
	Link.context([{type:'pages', params:{}}]);
	$scope.delPage=function(page){
		var data={
			action:'delPage',
			params:{page:page}
		};
		Link.ajax(data,function(){});		
	};
}]);

app.controller('modstoryCtl', ['$scope', '$window', '$http', '$location', '$routeParams', '$modal', 'FileUploader', 'hotkeys', 'Link', 'Data', function ($scope, $window, $http, $location, $routeParams, $modal, FileUploader, hotkeys, Link, Data) {
	$scope.key='story/'+$routeParams.id;
	Link.context([{type:$scope.key},{type:'groups'}]);
	$scope.tab={};
	$scope.tab.upload=1;
	$scope.tab.sons='A';
	$scope.position={A:0,B:0};
	$scope.colorThief=function(id){
		var img=document.images[id];
		var colorThief = new ColorThief();
		var colors=[];
		var colorsDef=[];
		angular.forEach(colorThief.getPalette(img, 4), function(c){
			var value=c[0]+c[1]+c[2];
			var color=rgb2hex('rgb('+c[0]+','+c[1]+','+c[2]+')');
			colors.push({value:value,color:color});
		});
		keysort(colors, "value desc");
		angular.forEach(colors, function(c){
			colorsDef.push(c.color);
		})
		Data.modele[$scope.key].couleur=colorsDef;
		$scope.modStory();
	};
	$scope.select=function(img){
		Data.modele[$scope.key].photos.une=img;
		$scope.modStory();
	};
	$scope.modStory=function(){
		if ($scope.dirty($scope.key)) {
			if (!Data.modele[$scope.key].photos.paires) Data.modele[$scope.key].photos.paires=[];
			if (Data.modele[$scope.key].photos.paires.length==0) Data.modele[$scope.key].photos.une='';
			else if (!Data.modele[$scope.key].photos.une) Data.modele[$scope.key].photos.une=Data.modele[$scope.key].photos.paires[0].gauche;
			var date=new Date(Data.modele[$scope.key].date).getTime()
			var sons=angular.copy(Data.modele[$scope.key].sons);
			sons.A.peaks=[];
			sons.B.peaks=[];
			var data={
				action:'modStory',
				params:{
					id:Data.modele[$scope.key].id,
					nom:Data.modele[$scope.key].nom,
					photos:Data.modele[$scope.key].photos,
					desc:Data.modele[$scope.key].desc,
					pitch:Data.modele[$scope.key].pitch,
					couleur:Data.modele[$scope.key].couleur,
					date:date,
					sons:sons
				}
			};
			Link.ajax(data,function(){});
		}
	}
	$scope.modStatut=function(){
		var data={
			action:'modStatut',
			params:{
				id:Data.modele[$scope.key].id,
				statut:Data.modele[$scope.key].statut
			}
		};
		Link.ajax(data,function(){});
	}
	$scope.delSub=function(face,uuid,lang){
		for (var i=0;i<Data.modele[$scope.key].sons[face].subs[lang].length;i++){
			if (Data.modele[$scope.key].sons[face].subs[lang][i].uuid==uuid) Data.modele[$scope.key].sons[face].subs[lang].splice(i,1);
		}
		$scope.modStory();
	}
	$scope.help=function(id){
		$modal.open({
			templateUrl: 'stories_partials/inc/help_'+id+'.html'
		});
	};
	$scope.modStoryInput=function(k,label){
		var verrou='story_'+k+'/'+$routeParams.id
		var m;
		if (k=='faceA') m=angular.copy(Data.modele[$scope.key].sons.A.titre);
		else if (k=='faceB') m=angular.copy(Data.modele[$scope.key].sons.B.titre);
		else m=angular.copy(Data.modele[$scope.key][k]);
		Link.set_verrou([verrou])
		var I={label:label,model:m};
		var modal = $modal.open({
			templateUrl: 'stories_partials/modinputmod.html',
			controller: 'modInputModCtl',
			resolve:{
				input: function () {
					return I;
				}
			}
		});

		modal.result.then(function (input) {
			if (k=='faceA') Data.modele[$scope.key].sons.A.titre=input.model;
			else if (k=='faceB') Data.modele[$scope.key].sons.B.titre=input.model;
			else Data.modele[$scope.key][k]=input.model;
			$scope.modStory();
			Link.del_verrou([verrou]);
		},function(){
			Link.del_verrou([verrou]);
		});
	}
	$scope.modSub=function(face,uuid,lang){
		var verrou='story_'+face+'_subs_'+lang+'_'+uuid+'/'+$routeParams.id
		var m;
		for (var i=0;i<Data.modele[$scope.key].sons[face].subs[lang].length;i++){
			if (Data.modele[$scope.key].sons[face].subs[lang][i].uuid==uuid) m=Data.modele[$scope.key].sons[face].subs[lang][i].text;
		}
		Link.set_verrou([verrou])
		var I={label:'soustitre',model:m};
		var modal = $modal.open({
			templateUrl: 'stories_partials/modinputmod.html',
			controller: 'modInputModCtl',
			resolve:{
				input: function () {
					return I;
				}
			}
		});

		modal.result.then(function (input) {
			for (var i=0;i<Data.modele[$scope.key].sons[face].subs[lang].length;i++){
				if (Data.modele[$scope.key].sons[face].subs[lang][i].uuid==uuid) Data.modele[$scope.key].sons[face].subs[lang][i].text=input.model;
			}
			$scope.modStory();
			Link.del_verrou([verrou]);
		},function(){
			Link.del_verrou([verrou]);
		});
	}
	$scope.modStoryDate=function(k,label){
		var verrou='story_'+k+'/'+$routeParams.id
		var m=angular.copy(Data.modele[$scope.key][k]);
		Link.set_verrou([verrou])
		var I={label:label,model:m};
		var modal = $modal.open({
			templateUrl: 'stories_partials/moddatemod.html',
			controller: 'modInputModCtl',
			resolve:{
				input: function () {
					return I;
				}
			}
		});

		modal.result.then(function (input) {
			Data.modele[$scope.key][k]=input.model;
			$scope.modStory();
			Link.del_verrou([verrou]);
		},function(){
			Link.del_verrou([verrou]);
		});
	}
	$scope.modStoryTexte=function(k,label){
		var verrou='story_'+k+'/'+$routeParams.id
		var m=angular.copy(Data.modele[$scope.key][k]);
		Link.set_verrou([verrou])
		var I={label:label,model:m};
		var modal = $modal.open({
			templateUrl: 'stories_partials/modtextemod.html',
			controller: 'modInputModCtl',
			resolve:{
				input: function () {
					return I;
				}
			}
		});

		modal.result.then(function (input) {
			Data.modele[$scope.key][k]=input.model;
			$scope.modStory();
			Link.del_verrou([verrou]);
		},function(){
			Link.del_verrou([verrou]);
		});
	}
	$scope.modStoryColor=function(k,label){
		var verrou='story_'+k+'/'+$routeParams.id
		var m=angular.copy(Data.modele[$scope.key][k]);
		Link.set_verrou([verrou])
		var I={label:label,model:m};
		var modal = $modal.open({
			templateUrl: 'stories_partials/modcolormod.html',
			controller: 'modInputModCtl',
			resolve:{
				input: function () {
					return I;
				}
			}
		});

		modal.result.then(function (input) {
			Data.modele[$scope.key][k]=input.model;
			$scope.modStory();
			Link.del_verrou([verrou]);
		},function(){
			Link.del_verrou([verrou]);
		});
	}
	$scope.delStory=function(story){
		var data={
			action:'delStory',
			params:{story:story}
		};
		Link.ajax(data,function(){
			$location.path('/stories');
		});
	}
	if (!($scope.key in $scope.uploaders)) {
		$scope.uploaders[$scope.key]={};
		$scope.uploaders[$scope.key].uploader = new FileUploader({
			url: 'upload',
			autoUpload:true,
			formData:[{id:$routeParams.id},{type:'story'}],
			onSuccessItem: function(item, response, status, headers) {}
		});
		$scope.uploaders[$scope.key].uploaderFaceA = new FileUploader({
			url: 'upload',
			autoUpload:true,
			formData:[{id:$routeParams.id},{type:'faceA'}],
			onSuccessItem: function(item, response, status, headers) {}
		});
		$scope.uploaders[$scope.key].uploaderFaceB = new FileUploader({
			url: 'upload',
			autoUpload:true,
			formData:[{id:$routeParams.id},{type:'faceB'}],
			onSuccessItem: function(item, response, status, headers) {}
		});
	}
	$scope.delFile=function(file){
		var data={
			action:'delFile',
			params:{
				id:$routeParams.id,
				file:file
			}
		};
		Link.ajax(data,function(){});
	}
	$scope.delP=function(e,i,s) {
		if (e.ctrlKey || e.shiftKey) {
			var pgauche=Data.modele[$scope.key].photos.paires[i].gauche;
			var pdroite=Data.modele[$scope.key].photos.paires[i].droite;
			if (pdroite=="" || pgauche=="") {
				Data.modele[$scope.key].photos.paires.splice(i,1);
				$scope.show[$scope.key]=Data.modele[$scope.key].photos.paires.length-1;
			} else {
				if (s==0) Data.modele[$scope.key].photos.paires[i].gauche="";
				if (s==1) Data.modele[$scope.key].photos.paires[i].droite="";
			}
			$scope.modStory();
		}
	}
	$scope.drop = function(e,d,i,gd,c){
		if (c=="photo") {
			if (gd==0) {
				Data.modele[$scope.key].photos.paires.push({gauche:d.filename,droite:''});
				$scope.show[$scope.key]=Data.modele[$scope.key].photos.paires.length-1;
			} else {
				if (gd==1) Data.modele[$scope.key].photos.paires[i].gauche=d.filename;	
				if (gd==2) Data.modele[$scope.key].photos.paires[i].droite=d.filename;	
			}
			$scope.modStory();
		}
		if (c=="gauche" || c=="droite") {
			var tmp=Data.modele[$scope.key].photos.paires[i].gauche;
			Data.modele[$scope.key].photos.paires[i].gauche=Data.modele[$scope.key].photos.paires[i].droite;	
			Data.modele[$scope.key].photos.paires[i].droite=tmp;	
			$scope.modStory();
		}
	};
	$scope.addtodiap=function(i,e){
		if (e.ctrlKey || e.shiftKey){
			Data.modele[$scope.key].photos.paires.push({gauche:i.filename,droite:''});
			$scope.show[$scope.key]=Data.modele[$scope.key].photos.paires.length-1;
		}
	}
	$scope.move = function(e,oldI,newI){
		oldI= oldI>0 ? oldI : 0 ;
		newI= newI>0 ? newI : 0 ;
		var paire=Data.modele[$scope.key].photos.paires[oldI];
		Data.modele[$scope.key].photos.paires.splice(oldI,1);
		Data.modele[$scope.key].photos.paires.splice(newI,0,paire);
		$scope.show[$scope.key]=newI;
		$scope.modStory();
	};
	$scope.next=function(){
		$scope.show[$scope.key]=($scope.show[$scope.key]+1)%Data.modele[$scope.key].photos.paires.length;
	}
	$scope.prev=function(){
		if ($scope.show[$scope.key]==0) $scope.show[$scope.key]=Data.modele[$scope.key].photos.paires.length-1;
		else $scope.show[$scope.key]--;
	}
	$scope.used=function(f){
		var res=false;
		angular.forEach(Data.modele[$scope.key].photos.paires,function(p){
			if (p.gauche==f.filename || p.droite==f.filename) res=true;
		});
		return res;
	};
	$scope.forms={};
	$scope.imgDroit=function(f){
		$scope.studio.droit=f;
	}
	$scope.imgGauche=function(f){
		$scope.studio.gauche=f;
	}
	$scope.uploadCustom=function(f){
		$scope.uploader.addToQueue([f]);
	}
	$scope.$watch('Data.modele["'+$scope.key+'"].statut',function(n,o){
		if (typeof o != "undefined") $scope.modStatut();
	});
	$scope.toggle_acl_group=function(g){
		if (Data.modele[$scope.key].groups.indexOf(g.id)>=0) Link.ajax({action:'delAcl',params:{type_ressource:'stories',id_ressource:$routeParams.id,type_acces:'group',id_acces:g.id,level:3}});
		else Link.ajax({action:'addAcl',params:{type_ressource:'stories',id_ressource:$routeParams.id,type_acces:'group',id_acces:g.id,level:3}});
	}
	hotkeys.bindTo($scope)
	.add({
		combo: 'right',
		description: 'Voir photos suivantes',
		callback: $scope.next
	})
	.add({
		combo: 'left',
		description: 'Voir photos précédentes',
		callback: $scope.prev
	});
	angular.element($window).on('scroll',debounce(function(){
		if (angular.element(".maindiap").length>0) {
			var pos=angular.element(".maindiap").parent().offset().top;
			var height=angular.element(".maindiap").height();
			var spos=angular.element(".serverfiles").offset().top;
			var sheight=angular.element(".serverfiles").height();
			var scroll=angular.element($window).scrollTop();
			var d=150;
			if (pos+height-scroll<d && spos+sheight-scroll>2*d) {
				angular.element(".maindiap").clearQueue().animate({top:scroll+d-(pos+height)},500);
			} else {
				angular.element(".maindiap").clearQueue().animate({top:0},500);
			}
		}
	},100));

	$scope.$on("$destroy", function(){
		angular.element($window).off('scroll');
	});
}]);
app.controller('modpageCtl', ['$scope', '$http', '$location', '$routeParams', '$modal', 'Link', 'Data', function ($scope, $http, $location, $routeParams, $modal, Link, Data) {
	$scope.key='page/'+$routeParams.id;
	Link.context([{type:$scope.key}],[$scope.key]);
	$scope.modPage=function(){
		if ($scope.dirty($scope.key)) {
			$scope.wait=true;
			var data={
				action:'modPage',
				params:{
					id:Data.modele[$scope.key].id,
					nom:Data.modele[$scope.key].nom,
					html:Data.modele[$scope.key].html,
					statut:Data.modele[$scope.key].statut
				}
			};
			Link.ajax(data,function(){
				$scope.updatePage();
				$scope.wait=false;
			});
		}
	}
	$scope.forms={};
	$scope.$watch('Data.modele["'+$scope.key+'"].statut',function(o,n){
		if (o!=n) $scope.modPage();
	});
	$scope.$on("$destroy", function(){
		Link.del_verrou([$scope.key]);
	});
}]);
//admin
app.controller('adminCtl', ['$scope', '$http', '$location', 'Data', 'Link', function ($scope, $http, $location, Data, Link) {
	$scope.Data=Data;
	Link.context([{type:'users', params:{}},{type:'groups', params:{}}]);
	$scope.done=false;
	$scope.history=[];
	$scope.users=[];
	$scope.currentPage=1;
	$scope.currentPageU=1;
	$scope.delUser=function(id){
		var data={
			action:'delUser',
			params:{id:id}
		};
		Link.ajax(data,function(data){});
	};
	$scope.delGroup=function(id){
		var data={
			action:'delGroup',
			params:{id:id}
		};
		Link.ajax(data,function(data){});
	};
	$scope.routeVerb=function (verb) {
		var tab=verb.replace(/\W+/g, '-')
		.replace(/([a-z\d])([A-Z])/g, '$1-$2').split('-');
		return tab[1].toLowerCase();
	}
	$scope.dump=function (o) {
		return JSON.stringify(o, null, 4)
	}
}]);
app.controller('addUserCtl', ['$scope', '$http', '$location', 'Data', 'Link', function ($scope, $http, $location, Data, Link) {
	$scope.Data=Data
	Link.context([{type:'users', params:{}}]);
	$scope.newUser={};
	$scope.addUser=function(){
		var data={
			action:'addUser',
			params:{
				name:$scope.newUser.name,
				login:$scope.newUser.login,
				pwd:$scope.newUser.pwd
			}
		};
		Link.ajax(data,function(m){
			$location.path('/admin');
		});
	};
	$scope.loginExists= function(login){
		var test=false;
		angular.forEach(Data.modele.users,function(u){
			if (u.login==login){
				test=true;
			}
		});
		return test;
	}
}]);
app.controller('addGroupCtl', ['$scope', '$http', '$location', 'Data', 'Link', function ($scope, $http, $location, Data, Link) {
	$scope.Data=Data
	Link.context([{type:'groups', params:{}}]);
	$scope.newGroup={};
	$scope.addGroup=function(){
		var data={
			action:'addGroup',
			params:{
				nom:$scope.newGroup.nom,
			}
		};
		Link.ajax(data,function(m){
			$location.path('/admin');
		});
	};
	$scope.groupExists= function(nom){
		var test=false;
		angular.forEach(Data.modele.groups,function(g){
			if (g.nom==nom){
				test=true;
			}
		});
		return test;
	}
}]);
app.controller('moiCtl', ['$scope', '$http', '$location', '$timeout', 'Data', 'Link', function ($scope, $http, $location, $timeout, Data, Link) {
	$scope.key='user/'+Data.modele.myid;
	Link.context([{type:'groups'},{type:'usersall', params:{}}],[$scope.key]);
	$scope.u={};
	$timeout(function(){
        	$scope.u.id=Data.modele.myid;
		$scope.u.name=Data.modele.usersall[Data.modele.myid].name;
		$scope.u.login=Data.modele.usersall[Data.modele.myid].login;
	},500);
	$scope.mod=function(){
		var data={
			action:'modMoi',
			params:{
				id:$scope.u.id,
				login:$scope.u.login,
				name:$scope.u.name,
				pwd:$scope.u.pwd
			}
		};
		Link.ajax(data,function(data){
			$location.path('/');
		});
	};
	$scope.$on("$destroy", function(){
		Link.del_verrou([$scope.key]);
	});
}]);
app.controller('modUserCtl', ['$scope', '$http', '$location', '$routeParams', '$timeout', 'Data', 'Link', function ($scope, $http, $location, $routeParams, $timeout, Data, Link) {
	$scope.key='user/'+$routeParams.id;
	if (Data.modele[$scope.key]) Link.del($scope.key);
    	$timeout(function(){
		Link.context([{type:'users'},{type:'groups'},{type:$scope.key,force:1}],[$scope.key]);	
        },500);
	$scope.data=Data;
	$scope.mod=function(){
		var data={
			action:'modUser',
			params:{
				id:Data.modele[$scope.key].id,
				login:Data.modele[$scope.key].login,
				name:Data.modele[$scope.key].name,
				pwd:Data.modele[$scope.key].pwd,
				role:Data.modele[$scope.key].role
			}
		};
		Link.ajax(data,function(data){
			$location.path('/admin');
		});
	};
	$scope.toggle_group=function(g){
		if (g.users && g.users.indexOf(Data.modele[$scope.key].id)>=0) Link.ajax({action:'delUserGroup',params:{userid:$routeParams.id,groupid:g.id}});
		else Link.ajax({action:'addUserGroup',params:{userid:$routeParams.id,groupid:g.id}});
	}
	$scope.$on("$destroy", function(){
		Link.del_verrou([$scope.key]);
	});
}]);
app.controller('modGroupCtl', ['$scope', '$http', '$location', '$routeParams', 'Data', 'Link', function ($scope, $http, $location, $routeParams, Data, Link) {
	$scope.key='group/'+$routeParams.id;
    	Link.context([{type:'users'},{type:'groups'},{type:$scope.key}],[$scope.key]);
	$scope.data=Data;
	$scope.mod=function(){
		var data={
			action:'modGroup',
			params:{
				id:Data.modele[$scope.key].id,
				nom:Data.modele[$scope.key].nom
			}
		};
		Link.ajax(data,function(data){
			$location.path('/admin');
		});
	};
	$scope.toggle_group=function(u){
		if (Data.modele[$scope.key].users && Data.modele[$scope.key].users.indexOf(u.id)>=0) Link.ajax({action:'delUserGroup',params:{userid:u.id,groupid:$routeParams.id}});
		else Link.ajax({action:'addUserGroup',params:{userid:u.id,groupid:$routeParams.id}});
	}
	$scope.$on("$destroy", function(){
		Link.del_verrou([$scope.key]);
	});
}]);
app.controller('addConstanteCtl', ['$scope', '$http', '$location', '$routeParams', 'Data', function ($scope, $http, $location, $routeParams, Data) {
	$scope.c={k:'',v:''}
	$scope.mod=function(){
		var data={
			action:'addConstante',
			params:{
				id:$scope.c.k,
				v:$scope.c.v
			}
		};
		Link.ajax(data,function(data){
			$location.path('/admin');
		});
	};
}]);
app.controller('modConstanteCtl', ['$scope', '$http', '$location', '$routeParams', 'Data', 'Link', function ($scope, $http, $location, $routeParams, Data, Link) {
	$scope.k=$routeParams.id;
	$scope.data=Data;
	$scope.mod=function(){
		var data={
			action:'modConstante',
			params:{
				k:$scope.k,
				v:Data.modele.constantes[$scope.k]
			}
		};
		Link.ajax(data,function(data){
			$location.path('/admin');
		});
	};
}]);
app.controller('addStoryModCtl', ['$scope', '$modalInstance', '$modal', 'story', function ($scope, $modalInstance, $modal, story) {
	$scope.story=story;
	$scope.form={};
	$scope.ok = function () {
		if ($scope.form.addStory.$valid){
			$modalInstance.close($scope.story);
		}
	};
	$scope.cancel = function () {
		$modalInstance.dismiss();
	};
}]);
app.controller('addPageModCtl', ['$scope', '$modalInstance', '$modal', 'page', function ($scope, $modalInstance, $modal, page) {
	$scope.page=page;
	$scope.form={};
	$scope.ok = function () {
		if ($scope.form.addPage.$valid){
			$modalInstance.close($scope.page);
		}
	};
	$scope.cancel = function () {
		$modalInstance.dismiss();
	};
}]);
app.controller('modInputModCtl', ['$scope', '$modalInstance', '$modal', 'input',function ($scope, $modalInstance, $modal, input) {
	$scope.input=input;
	$scope.form={};
	$scope.ok = function () {
		if ($scope.form.input.$valid){
			$modalInstance.close($scope.input);
		}
	};
	$scope.cancel = function () {
		$modalInstance.dismiss();
	};
}]);
app.filter('startFrom', function() {
		return function(input, start) {
				start = +start; //parse to int
				return input.slice(start);
		}
});
app.filter('hasDonnee', function() {
		return function(cass) {
	var res=[];
				angular.forEach(cass, function(cas){
		if (cas.donnees.length>0) res.push(cas);
	});
				return res;
		}
});
app.filter('exists', function() {
		return function(ee) {
	var res=[];
				angular.forEach(ee, function(e){
		if (e.id>0) res.push(e);
	});
				return res;
		}
});
app.filter('image', function() {
		return function(pjs) {
	var res=[];
				angular.forEach(pjs, function(pj){
		if (pj.mime=="image/png" || pj.mime=="image/jpeg") res.push(pj);
	});
				return res;
		}
});
app.filter('nl2br', function() {
		var span = document.createElement('span');
		return function(input) {
				if (!input) return input;
				var lines = input.split('\n');

				for (var i = 0; i < lines.length; i++) {
						span.innerText = lines[i];
						span.textContent = lines[i];
						lines[i] = span.innerHTML;
				}
				return lines.join('<br />');
		}
});
