$('.game').click(function(event)
{
	event.preventDefault();
	
	$.ajax
	({
		url: $(this).find('.game-link').attr('href'),
		type: 'get',
		success: function(result)
		{
			var json = $.parseJSON(result)
			$('#status').html(json.message);
		}
	});
});

var source = new EventSource("/status");
source.onmessage = function(event) {
	var json = $.parseJSON(event.data);
	if (json.status != 0) {
		$('#status').addClass('error');
	} else
		$('#status').removeClass('error');
	$("#status").html(json.message);
};