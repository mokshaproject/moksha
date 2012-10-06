<%namespace name="tw" module="tw2.core.mako_util"/>
% for c in tw._('children'):
	${c.display(url=tw._('url'))}
% endfor
