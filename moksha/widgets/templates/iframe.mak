<%namespace name="tw" module="moksha.utils.mako"/>
<h1>${tw._('title')}</h1>
<iframe id="${tw._('id')}" src="${tw.('url')}" width="${tw._('width')}" height="${tw._('height')}">
<p>Your browser does not support iframes.</p>
</iframe>
