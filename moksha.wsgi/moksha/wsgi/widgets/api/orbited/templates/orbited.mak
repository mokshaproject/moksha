<%namespace name="tw" module="tw2.core.mako_util"/>
<script type="text/javascript">
    Orbited.settings.hostname = '${tw._("orbited_host")}';
    Orbited.settings.port = ${str(tw._("orbited_port"))};
    document.domain = document.domain
    TCPSocket = Orbited.TCPSocket
    connect = function() {
        conn = new TCPSocket()
        conn.onread = ${tw._("onread")}
        conn.onopen = ${tw._("onopen")}
        conn.onclose = ${tw._("onclose")}
        conn.open('${tw._("orbited_host")}',
				   ${str(tw._("orbited_port"))})
    }
    $(document).ready(function() {
        connect()
    })
</script>
