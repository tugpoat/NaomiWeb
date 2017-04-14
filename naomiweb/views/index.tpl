% include('header.tpl', title='NetDIMM Loader')

<div class="container">
	% include('navbar.tpl', activePage='games')
  	
	% if defined('games'):
	<p>Choose a game to play</p>
	% for game in games:
		<p class="game">
			<a class="game-link {{game.status}}" href="load/{{game.checksum}}">{{game.name}}</a> <span class="label label-default">{{round(game.size/float(1024*1024), 1)}} MB</span>
		</p>
	% end
	% end
	% for f in filters:
		<span>{{f[0]}} = {{f[1]}}</span>
	% end

	% if not defined('games'):
	<div class="alert alert-danger"><span class="glyphicon glyphicon-warning-sign"></span> No games were found! Verify that the directory set on the configuration screen exists and contains valid NAOMI games.</div>
	% end

</div>

% include('footer.tpl')
