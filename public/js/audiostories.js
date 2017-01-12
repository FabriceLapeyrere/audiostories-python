$(document).ready(function() {
	$(".story-big, .story-small").mouseenter(function(){
		var i=$(this).attr('data-id');
		for(var j=0;j<$(".story-big, .story-small").length;j++){
			$('.color-'+j).removeClass('opaque');
		}
		$('.color-'+i).addClass('opaque');
	});
	if($('.newsok').length>0) {
		window.setTimeout(function(){
			$('.newsok').fadeOut(function(){window.location='/'});
		},5000);
	}
});
