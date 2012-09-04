<%namespace name="tw" module="tw2.core.mako_util"/>
% for child in tw._('c'):
	${child.display() | n}
% endfor
<script type="text/javascript">
  moksha_base_url = "${str(tw._('base_url'))}";
  moksha_userid = "${str(tw._('user_id'))}";
  moksha_debug = ${str(tw._('debug'))};
  moksha_profile = ${str(tw._('profile'))};
</script>
