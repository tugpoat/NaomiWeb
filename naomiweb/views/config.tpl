% include('header.tpl', title='Configure')

<div class="container">
	% include('navbar.tpl', activePage='config')

	% if defined('did_config'):
	<div class="alert alert-success"><span class="glyphicon glyphicon-ok"></span> Saved configuration!</div>
	%end

	<form class="form-horizontal" action="config" method="POST" role="form">
		<h2>Network</h2>
		<div class="row container">
			<div class="form-group">
				<label class="col-sm-2 control-label">IP Address</label>
				<div class="col-sm-3">
					<input type="text" class="form-control" name="network_ip" value="{{network_ip}}" placeholder="IP Address" />
				</div>
			</div>

			<div class="form-group">
				<label class="col-sm-2 control-label">Subnet Mask</label>
				<div class="col-sm-3">
					<input type="text" class="form-control" name="network_subnet" value="{{network_subnet}}" placeholder="Subnet Mask" />
				</div>
			</div>
		</div>

		<h2>Games</h2>
		<div class="row container">
			<div class="form-group">
				<label class="col-sm-2 control-label">Directory</label>
				<div class="col-sm-3">
					<input type="text" class="form-control" name="games_directory" value="{{games_directory}}" placeholder="Directory" />
				</div>
			</div>

			<div class="form-group">
				<label class="col-sm-2 control-label">Region</label>
				<div class="col-sm-3">
					<select class="form-control" name="selRegion">
						%if games_region == 'japan':
							<option value='japan' selected>Japan</option>
						%else:
							<option value='japan'>Japan</option>
						%end
						%if games_region == 'usa':
							<option value='usa' selected>USA</option>
						%else:
							<option value='usa'>USA</option>
						%end
						%if games_region == 'euro':
							<option value='euro' selected>Europe</option>
						%else:
							<option value='euro'>Europe</option>
						%end
						%if games_region == 'asia':
							<option value='asia' selected>Asia</option>
						%else:
							<option value='asia'>Asia</option>
						%end
						%if games_region == 'australia':
							<option value='australia' selected>Australia</option>
						%else:
							<option value='australia'>Australia</option>
						%end
					</select>
				</div>
			</div>
		</div>

		<h2>Filters</h2>
		<div class="row container">
			<div class="form-group">
				<label class="col-sm-2 control-label"></label>
				<div class="col-sm-3">
					% for f in filters:
					<select class="form-control" name="sel-{{f[0]}}">

					</select>
					% end
				</div>
			</div>
		</div>

		<div class="row container">
			<div class="col-md-2">
				<button type="submit" class="btn btn-default">Save</button>
			</div>
		</div>
	</form>
</div>

% include('footer.tpl')
