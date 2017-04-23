% include('header.tpl', title='NetDIMM Loader')

<div class="container">
	% include('navbar.tpl', activePage='games')
  	
	% if defined('games'):
	<p>Choose a game to play</p>
	% for game in games:
		<div class="label label-default game">
			<div class="col0">
				<img src="/static/images/{{game.id}}.jpg" />
			</div>
			<div class="col1">
				<div><a class="game-link {{game.status}}" href="load/{{game.checksum}}">{{game.name}}</a></div>
				<div><em>{{game.filename}}</em> <span class="label label-default fileinfo">{{round(game.size/float(1024*1024), 1)}} MB</span></div>
			</div>
			
		</div>
	% end
	% end
	% for f in activefilters:
		<span>{{f[0]}} = {{f[1]}}</span>
	% end

	% if not defined('games'):
	<div class="alert alert-danger"><span class="glyphicon glyphicon-warning-sign"></span> No games were found! Verify that the directory set on the configuration screen exists and contains valid NAOMI games.</div>
	% end

</div>

% include('footer.tpl')
