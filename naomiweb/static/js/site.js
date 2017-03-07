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

setInterval(function() {
	$.ajax
	({
		url: '/status',
		type: 'get',
		success: function(result)
		{
			var json = $.parseJSON(result)
			if (json.status != 0) {
				$('#status').addClass('error');
			} else
				$('#status').removeClass('error');
			$('#status').html(json.message);
		}
	});
}, 1000);