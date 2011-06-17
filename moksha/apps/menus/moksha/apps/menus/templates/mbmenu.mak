<%namespace name="tw" module="moksha.utils.mako"/>
<table  border="0" cellpadding="0" cellspacing="0" bgcolor="#EDEDED">
    <tr>
        <td valign="bottom">
            <table  border="0" cellpadding="0" cellspacing="0" bgcolor="#FFFFFF" class="container">
                <tr>
                    <td class="${tw._('id')}" align="right">

                        <table class="${tw._('rootMenuSelector')}" cellspacing='0' cellpadding='0' border='0'><tr>
                            % for menu_id, menu in tw._('menus'):
                                <td menu="${tw._('id')}_${menu_id}">${menu}</td>
                            % endfor
                        </tr></table>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>

