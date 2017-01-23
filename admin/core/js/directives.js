app.directive('sticky', ['$timeout', function($timeout){
	return {
		restrict: 'A',
		scope: {
			offset: '@',
			stickyClass: '@'
		},
		link: function($scope, $elem, $attrs){
			$timeout(function(){
				var offsetTop = $scope.offset || 0,
					stickyClass = $scope.stickyClass || '',
					$window = angular.element(window),
					doc = document.documentElement,
					initialPositionStyle = $elem.css('position'),
					stickyLine,
					scrollTop;


				// Set the top offset
				//
				$elem.css('top', offsetTop+'px');


				// Get the sticky line
				//
				function setInitial(){
					stickyLine = $elem[0].offsetTop - offsetTop;
					checkSticky();
				}

				// Check if the window has passed the sticky line
				//
				function checkSticky(){
					scrollTop = (window.pageYOffset || doc.scrollTop)  - (doc.clientTop || 0);

					if ( scrollTop >= stickyLine ){
						$elem.addClass(stickyClass);
						$elem.css('position', 'fixed');
					} else {
						$elem.removeClass(stickyClass);
						$elem.css('position', initialPositionStyle);
					}
				}


				// Handle the resize event
				//
				function resize(){
					$elem.css('position', initialPositionStyle);
					$timeout(setInitial);
				}


				// Attach our listeners
				//
				$window.on('scroll', checkSticky);
				
				setInitial();
			});
		},
	};
}]);
app.directive('onScroll', function($timeout) {
    return {
        scope: {
            onScroll: '&onScroll',
        },
        link: function(scope, element) {
            var scrollDelay = 250,
                scrollThrottleTimeout,
                throttled = false,
                scrollHandler = function() {
                    if (!throttled) {
                        scope.onScroll();
                        throttled = true;
                        scrollThrottleTimeout = $timeout(function(){
                            throttled = false;
                        }, scrollDelay);
                    }
                };

            element.on("scroll", scrollHandler);

            scope.$on('$destroy', function() {
                element.off('scroll', scrollHandler);
            });
        }
    };
});
app.directive('autoFocus', function($timeout) {
    return {
        restrict: 'AC',
        link: function(_scope, _element) {
            $timeout(function(){
                _element[0].focus();
	    }, 500);
        }
    };
});
app.directive('loading', function($timeout) {
    return {
        restrict: 'A',
        template: "<div class='loader-container' ng-if='wait'><img class='loader' src='img/loader.gif' /></div><div ng-if='!wait' class='cache'><ng-transclude></ng-transclude></div>",
        transclude: true,
        scope:{data:'=', loading:'='},
        link: function(scope, element, attrs) {
            element.children('.cache').removeClass("cache");
            scope.wait=true;
            scope.$watchCollection('data',function(){
                if(scope.data.modele[scope.loading]) scope.wait=false;
            })
        }
    };
});
app.directive("deferredCloak", function () {
    return {
        restrict: 'A',
        link: function (scope, element, attrs) {       
            attrs.$set("deferredCloak", undefined);
            element.removeClass("deferred-cloak");
        }
    };
});
app.directive('locked', [
	function(){
		return {
            template: "<div ng-class=\"{lockedWrap:verrou!='none' && verrou!=data.modele.mypeer}\">\n"+
                "<div ng-class=\"{locked:verrou!='none' && verrou!=data.modele.mypeer}\" ng-transclude></div>\n"+
                "<span ng-if=\"verrou!='none' && verrou!=data.modele.mypeer\" class='locked-by'>{{data.modele.usersall[data.modele.peers[verrou].userid].name}} modifie ceci ... </span>\n"+
                "</div>\n",
            restrict: 'E',
            scope: {
                data: '=',
                verrou: '='
            },
            transclude:true
		}
	}
]);
app.directive('waveform', [ '$window', '$interval', '$timeout', 
	function($window, $interval, $timeout){
		return {
			templateUrl: 'partials/inc/waveform.html',
			restrict: 'E',
			controller:['$scope','$element', function($scope, $element){
				$scope.txts={subs:'',clock:''};
				$scope.controlSub=function(uuid,e){
					if (e.ctrlKey || e.shiftKey){
						if (confirm('sûr ?')) $scope.delsub($scope.face,uuid,$scope.lang);
					} else {
						angular.element('.main-waveform').trigger('mouseleave');
						$scope.modsub($scope.face,uuid,$scope.lang);
					}
				}
				$scope.zoom=100;
				$scope.modzoom=function(e,d){
					if (e.ctrlKey || e.shiftKey){
						if (d<0) $scope.zoomin();
						if (d>0) $scope.zoomout();
						e.preventDefault();
					}
 				};
				$scope.zoomin=function(){
					$scope.zoom=$scope.zoom*1.2>500 ? 500 : $scope.zoom*1.2;
					$scope.redraw();
				};
				$scope.zoomout=function(){
					$scope.zoom=$scope.zoom/1.2<100 ? 100 : $scope.zoom/1.2;
					$scope.redraw();	
				};
				$scope.playpause=function(){
					if ($scope.wavesurfer.isPlaying) $scope.wavesurfer.pause();
					else $scope.wavesurfer.play();
				};
				$scope.marks={d:-1,f:-1};
				$scope.check_parts=function(mod){
					var tri=function(a,b)
					{
						return a.start-b.start
					}
					var parts=$scope.srt[$scope.lang];
					var d=$scope.marks.d;
					var f=$scope.marks.f;
					parts.sort(tri);
					if (mod && (d==-1 || f==-1)){
						for (var i=0;i<parts.length;i++){
							if (d>=0 && (i==0 && d<parts[0].start || i>0 && d>parts[i-1].end && d<parts[i].start)) {
								parts[i].start=d;
								d=-1;
								f=-1;
								break;
							}
							if (f>=0 && (i==parts.length-1 && f>parts[parts.length-1].end || i<parts.length-1 && f<parts[i+1].start && f>parts[i].end)) {
								parts[i].end=f;
								d=-1;
								f=-1;
								break;
							}
						}
					}
					for (var i=0;i<parts.length;i++){
						if (d>=0 && f>=0 && d<parts[i].start && f>parts[i].end ) {
							d=-1;
							f=-1;
							break;
						}
					}
					for (var i=0;i<parts.length;i++){
						if (d>=0 && d>parts[i].start && d<parts[i].end ) {
							parts[i].start=d;
							d=-1;
							f=-1;
							break;
						}
						if (f>=0 && f>parts[i].start && f<parts[i].end ) {
							parts[i].end=f;
							d=-1;
							f=-1;
							break;
						}
					}
					if (d>=0 && d<f){
						u=1;
						for (var i=0;i<parts.length;i++){
							if (parts[i].uuid>=u) {
								u=parts[i].uuid+1;
							}
						}
						parts.push({start:d,end:f,duration:$scope.wavesurfer.getDuration(),uuid:u,text:''});
						d=-1;
						f=-1;
					}
					$scope.marks.d=d;
					$scope.marks.f=f;
					$scope.srt[$scope.lang]=parts;
					$scope.action();
				}
				$scope.keys=function(e){
					var mod=false;
					if (e.ctrlKey || e.shiftKey) {
						mod=true;
					} else {
						mod=false;
					}
					if (e.keyCode == 68) {
						$scope.marks.d=$scope.wavesurfer.getCurrentTime();
						$timeout(function(){$scope.check_parts(mod);},0);
					}
					if (e.keyCode == 70) {
						$scope.marks.f=$scope.wavesurfer.getCurrentTime();
						$timeout(function(){$scope.check_parts(mod);},0);
					}
					if (e.keyCode == 27) {
						d=-1;
						f=-1;
						$scope.check_parts(mod);
					}
					if (e.keyCode == 32) {
						if ($scope.wavesurfer.isPlaying) $scope.wavesurfer.pause();
						else $scope.wavesurfer.play();
						e.preventDefault(mod);
					}
				};
				$scope.$watch("peaks", function(p) {
					if ($scope.peaks!=p) {
						console.log('new peaks');
						$scope.peaks=p;
						var s= Smooth($scope.peaks);
						var arrayOfPeaks=[];
						for (var i=0;i<$scope.peaks.length*5;i++) {
							arrayOfPeaks.push(s(i/5));
						}
						$scope.wavesurfer.load($scope.file, arrayOfPeaks);
					}
				});
				$scope.$watch("srt", function(srt) {
					$scope.subprocess($scope.position);
				});
				$scope.subprocess=function(t){
					var parts=$scope.srt[$scope.lang];
					var sub='';
					for (var i=0;i<parts.length;i++){
						if (t>=parts[i].start && t<=parts[i].end ) {
							sub=parts[i].text;
						}
					}
					$scope.txts.subtext=sub;
				};
				$scope.process=function(t){
					if (t>=$scope.wavesurfer.getDuration()) {
						$scope.wavesurfer.isPlaying=false;
					}
					$scope.position=t;
					$scope.setclock(t);
					$scope.subprocess(t);
				};
				$scope.wavesurfer = Object.create(WaveSurfer);
				$scope.lang='fr';
				$scope.wavesurfer.init({
				    container: $element.find('.waveform')[0],
				    backend: 'AudioElement',
				    height:100,
				    cursorColor:'rgba(0,0,0,0.1)',
				    progressColor:'#333',
				    waveColor:'#AAA',
				    hideScrollbar:true
				});
				$scope.wavesurfer.isPlaying=false;
				$scope.wavesurfer.on('audioprocess',function(t){
					$timeout(function(){$scope.process(t);},0);
				});
				$scope.wavesurfer.on('play',function(){$scope.wavesurfer.isPlaying=true;});
				$scope.wavesurfer.on('pause',function(){$scope.wavesurfer.isPlaying=false;});
				$scope.setclock=function(t){
					var ts=Math.floor(t);
					var mins=Math.floor(ts/60);
					var s=ts%60;
					if (s<10) s='0'+s;
					var temps=mins+"'"+s+'"';
					var total=Math.floor($scope.wavesurfer.getDuration());
					var totalmins=Math.floor(total/60);
					var totals=total%60;
					if (totals<10) totals='0'+totals;
					var tempsTotal=totalmins+"'"+totals+'"';
					$scope.txts.clock=temps+" / "+tempsTotal;
				}
				$scope.wavesurfer.on('ready',function(){
					$scope.process(0);
				});
				$scope.redraw=function() {
					var rail= $element.find('.rail');
					var tiroir=$element.find('.tiroir');
					var Ap=$scope.wavesurfer.isPlaying;
					var percent=$scope.position/$scope.wavesurfer.getDuration();
					var w=rail.width();
					tiroir.css('width',$scope.zoom+'%');
					var wt=tiroir.width();
					rail.scrollLeft(Math.max(0,wt*percent-w/2));
					$scope.wavesurfer.empty();
					$scope.wavesurfer.drawBuffer();
					$scope.wavesurfer.seekTo(percent);
					if (Ap) $scope.wavesurfer.play();
				};
				angular.element($window).on('resize', $scope.redraw);
				$element.on('mouseenter',function(e){angular.element($window).on('keydown',$scope.keys);});
				$element.on('mouseleave',function(e){angular.element($window).off('keydown',$scope.keys);});
				$scope.waveinit=function(){
					var s= Smooth($scope.peaks);
					var arrayOfPeaks=[];
					for (var i=0;i<$scope.peaks.length*5;i++) {
						arrayOfPeaks.push(s(i/5));
					}
					$scope.wavesurfer.load($scope.file, arrayOfPeaks);
				}
				$scope.waveinit();
				$scope.$on("$destroy", function(){
					angular.element($window).off('resize', $scope.redraw);
					angular.element($window).off('keydown', $scope.keys);
				});
			}],
			scope: {
				face: '@',
				srt: '=',
				peaks: '=',
				action: '=',
				modsub: '=',
				delsub: '=',
				position: '=',
				file: '='
			}
		}
	}
]);


















app.directive('ngConfirmClick', [
	function(){
		return {
			restrict: 'A',
			link: function(scope, element, attrs){
				element.bind('click', function(e){
					var message = attrs.ngConfirmMessage;
					var action = attrs.ngConfirmClick;
					if(message && confirm(message)){
						scope.$eval(action);
					}
				});
			}
		}
	}
]);
app.directive('ngAllowTab', [
	function(){
		return {
			restrict: 'A',
			link: function(scope, element, attrs){
				element.bind('keydown', function(e){
					if (e.keyCode == 9) { // tab
						var input = this.value; // as shown, `this` would also be textarea, just like e.target
						var remove = e.shiftKey;
						var posstart = this.selectionStart;
						var posend = this.selectionEnd;
						// if anything has been selected, add one tab in front of any line in the selection
						if (posstart != posend) {
							posstart = input.lastIndexOf('\n', posstart) + 1;
							var compensateForNewline = input[posend-1] == '\n';
							var before = input.substring(0,posstart);
							var after = input.substring(posend-(compensateForNewline?1:0));
							var selection = input.substring(posstart,posend);

							// now add or remove tabs at the start of each selected line, depending on shift key state
							// note: this might not work so good on mobile, as shiftKey is a little unreliable...
							if (remove) {
								if (selection[0] == '\t') selection = selection.substring(1);
								selection = selection.split('\n\t').join('\n');
							} else {
								selection = selection.split('\n');
								if (compensateForNewline) selection.pop();
								selection = '\t'+selection.join('\n\t');
							}

							// put it all back in...
							this.value = before+selection+after;
							// reselect area
							this.selectionStart = posstart;
							this.selectionEnd = posstart + selection.length;
						} else {
							var val = this.value;
							this.value = val.substring(0,posstart) + '\t' + val.substring(posstart);
							this.selectionEnd = element.selectionStart = posstart + 1;
						}
						e.preventDefault(); // dont jump. unfortunately, also/still doesnt insert the tab.
					}
				});
			}
		}
	}
]);
app.directive('dynTpl', ['$compile',
	function($compile){
		return {
            restrict: 'A',
            scope: {
                tpl:'=',
                data:'='
            },
            link: function(scope,element,attrs) {
                scope.$watch('tpl',function(){
                    element.html(scope.tpl);
                    $compile(element.contents())(scope);
                });
            }
        };
    }
]);
app.directive('mobDblclick',
    function () {

        const DblClickInterval = 300; //milliseconds

        var firstClickTime;
        var waitingSecondClick = false;

        return {
            restrict: 'A',
            link: function (scope, element, attrs) {
                element.bind('click', function (e) {

                    if (!waitingSecondClick) {
                        firstClickTime = (new Date()).getTime();
                        waitingSecondClick = true;

                        setTimeout(function () {
                            waitingSecondClick = false;
                        }, DblClickInterval);
                    }
                    else {
                        waitingSecondClick = false;

                        var time = (new Date()).getTime();
                        if (time - firstClickTime < DblClickInterval) {
                            scope.$apply(attrs.mobDblclick);
                        }
                    }
                });
            }
        };
    });
app.directive("fileread", function () {
		return {
			scope: {
				fileread: "="
			},
			link: function (scope, element, attributes) {
				element.bind("change", function (e) {
 		var files=scope.fileread;
		for(var i=0; i<e.target.files.length; i++) {
			files.push(e.target.files[i]);
			scope.$apply(function () {
				scope.fileread = files;
			});
		}
		
				});

			}
		}
	});
app.directive("imgCustom", function () {
		return {
			scope: {
				imgCustom: "=",
				imgCustomW: "=",
				imgCustomR: "="
			},
			link: function (scope, element, attributes) {
		scope.$watch('imgCustom',function(){
			loadImage(
				scope.imgCustom,
				function (img) {
					scope.$apply(function () {
						element.find('canvas').remove();
						element.append(img);
						element.find('canvas').addClass('img-responsive');
					});
				},
				{
					maxWidth: scope.imgCustomW,
					maxHeight: Math.floor(scope.imgCustomW/scope.imgCustomR),
					crop:true
				} // Options
			);
		});
			}
		}
	});

