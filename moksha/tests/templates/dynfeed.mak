<%namespace name="tw" module="moksha.utils.mako"/>
% for c in tw._('children'):
	${c.display(url=tw._('url'))}
% endfor
