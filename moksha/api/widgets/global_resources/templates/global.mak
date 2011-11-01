<%namespace name="tw" module="moksha.utils.mako"/>
% for child in tw._('c'):
	${str(child.display()) | n}
% endfor
<script type="text/javascript">
  moksha_base_url = "${tw._('base_url')}";
  moksha_csrf_token = "${tw._('csrf_token')}";
  moksha_csrf_trusted_domains = ${tw._('csrf_trusted_domains')};
  moksha_userid = "${tw._('user_id')}";
  moksha_debug = ${tw._('debug')};
  moksha_profile = ${tw._('profile')};
</script>
