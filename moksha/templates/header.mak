<%def name="header()">
<div class="span-24 top">
  ${tmpl_context.menu_widget()}

## <a href="/"><img src="/images/moksha-logo-small.png"/></a>
## <hr class="space">

##% if tmpl_context.auth('not_anonymous()'):
##	<div id="login-toolbar">
##		<form class="login_button" action="/logout">
##			Logged In: <span class="username"><a href="/profile">${tmpl_context.identity['person']['human_name']}</a></span>
##			<input type="submit"  class="button" value="Log Out" />
##		</form>
##	</div>
##% else:
##	<div id="login-toolbar">
##		<form onSubmit="$('#main_app').load('/appz/login?view=canvas'); return false;">
##			You are not logged in yet  <input type="submit"  value="Login" class="button"/>
##		</form>
##	</div>
##% endif

</div>
</%def>
