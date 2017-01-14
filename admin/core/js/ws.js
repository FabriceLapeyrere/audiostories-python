'use strict';
var myws= angular.module('myws', ['ngWebSocket']);
myws.value('Data', {
	uid: Math.random().toString(36).substr(2, 9),
	contexts:[],
	modele:{},
	modeleSrv:{},
	modeleFresh:true,
	max_contexts_length:20,
	offline:false,
	locked:false,
	logged:false
});
myws.factory('Link',['Data', '$websocket', '$window', '$http', function(Data, $websocket, $window, $http) {
	var link={};
	
	var loc = $window.location, new_uri, ws;
	if (loc.protocol === "https:") {
		new_uri = "wss:";
	} else {
		new_uri = "ws:";
	}
	new_uri += "//" + loc.host + "/admin/ws/";
	//console.log(new_uri);
	ws = $websocket(new_uri);
	ws.onMessage(function(event) {
		var res = JSON.parse(event.data);
		//console.log('message: ', res);
		if (res.type=="modele") {
			angular.forEach(res.collection, function(v,k){
				Data.modele[k]=v;
				Data.modeleSrv[k]=angular.copy(v);
			});
		}
		if (res.type=="logout") {
			$window.location="/admin/logout";
		}
	});
	ws.onError(function(event) {
		console.log('connection Error', event);
	});
	ws.onClose(function(event) {
		$window.location="/admin/index";
		console.log('connection closed', event);
	});
	ws.onOpen(function() {
		console.log('connection open');
	});
	link.status= function() {
			return ws.readyState;
		};
	link.send= function(message) {
			if (angular.isString(message)) {
				ws.send(message);
			}
			else if (angular.isObject(message)) {
				ws.send(JSON.stringify(message));
			}
		};
	link.ajax=function(data,callback){
		$http.post('ajax',data).then(callback);
	}
	link.del=function(k){
		Data.modele[k]={};
	}
	link.context=function(contexts,verrous){
		//console.log("update_contexts");
		Data.contexts=contexts;
		var haschat=false, hasconstantes=false, hasusers=false, hasusersall=false;
		for(var i=0;i<contexts.length;i++){
			if (contexts[i].type=='users') hasusers=true;
			if (contexts[i].type=='constantes') hasconstantes=true;
			if (contexts[i].type=='usersall') hasusersall=true;
			if (!contexts[i].params) contexts[i].params={};
		}
		if (!haschat) Data.contexts.push({type:'chat',params:{}});
		if (!hasusers) Data.contexts.push({type:'users',params:{}});
		if (!hasusersall) Data.contexts.push({type:'usersall',params:{}});
		if (!hasconstantes) Data.contexts.push({type:'constantes',params:{}});
		var actions=[{action:'update_contexts', contexts:Data.contexts}];
		if (verrous) {
			for(var i=0;i<verrous.length;i++){
				actions.push({action:'set_verrou', verrou:verrous[i]});
			}
		}
		link.send(actions);
	};
  	link.send=function(data){
		ws.send(JSON.stringify(data));
	};
	link.set_verrou = function(verrous) {
		var actions=[];
		for (var i=0; i<verrous.length;i++) {		
			actions.push({action:'set_verrou', verrou:verrous[i]});
		}
		link.send(actions);	
	}
	link.del_verrou = function(verrous) {
		var actions=[];
		for (var i=0; i<verrous.length;i++) {		
			actions.push({action:'del_verrou', verrou:verrous[i]});
		}
		link.send(actions);	
	};
	return link;
}]);
