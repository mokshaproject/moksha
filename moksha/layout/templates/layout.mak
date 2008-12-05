<div>
	<div id="container">
		<div id="header" class="ui-sortable">
			<h2>Header</h2>
			<dl class="sort">
				<dt>Pages</dt>
				<dd>Main Navigation</dd>
			</dl>
		</div>

		<div id="content" class="ui-sortable">
			<h2>Content</h2>
			% for widget in content:
	            <dl class="sort">
		    		<dt>${widget['name']}</dt>
				    <dd>${widget['widget']()}</dd>
 				</dl>
			% endfor
		</div>

		<div id="sidebar" class="ui-sortable">
			<h2>Sidebar</h2>
			<dl class="sort">
				<dt>Pages</dt>
				<dd>Mini About</dd>
			</dl>
			<dl class="sort">
				<dt>Blog</dt>
				<dd>Monthly Archives</dd>
			</dl>
			<dl class="sort">
				<dt>Links</dt>
				<dd>Random Links</dd>
			</dl>
		</div>

		<div class="clear"></div>

		<div id="footer" class="ui-sortable">
			<h2>Footer</h2>
			<dl class="sort">
				<dt>Pages</dt>
				<dd>Copyright</dd>
			</dl>
		</div>
	</div>

	<div id="meta">
		<div id="components" class="ui-sortable">
			<h2>Components</h2>
			<dl class="sort">
				<dt>Subheadline</dt>
				<dd>Paragraph</dd>
			</dl>
			<dl class="sort">
				<dd>Caption</dd>
			</dl>
		</div>

		<div id="trashcan" class="ui-sortable">
			<h2>Trash can</h2>
			<p>Drag modules here to delete them.</p>
		</div>
	</div>

	<div class="clear"></div>
	<div id="overlay">
		<div id="preloader"><img src="/toscawidgets/resources/moksha.widgets.layout.layout/static/loader.gif" alt="" /></div>
	</div>
</div>
