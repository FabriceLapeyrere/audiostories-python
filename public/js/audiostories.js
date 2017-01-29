$(document).ready(function() {
	$(".story-big, .story-small").mouseenter(function(){
		var i=$(this).attr('data-id');
		$(".story-big, .story-small").each(function(i,e){
			$('.color-'+$(e).attr('data-id')).removeClass('opaque');
		});
		$('.color-'+i).addClass('opaque');
	});
	if($('.newsok').length>0) {
		window.setTimeout(function(){
			$('.newsok').fadeOut(function(){window.location='/'});
		},5000);
	}
});
