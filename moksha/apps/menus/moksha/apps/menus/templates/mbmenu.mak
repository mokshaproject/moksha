<table  border="0" cellpadding="0" cellspacing="0" bgcolor="#EDEDED">
    <tr>
        <td valign="bottom">
            <table  border="0" cellpadding="0" cellspacing="0" bgcolor="#FFFFFF" class="container">
                <tr>
                    <td class="${id}" align="right">

                        <table class="${rootMenuSelector}" cellspacing='0' cellpadding='0' border='0'><tr>
                            % for menu_id, menu in menus:
                                <td menu="${id}_${menu_id}">${menu}</td>
                            % endfor
                        </tr></table>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>

