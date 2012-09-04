(function(){

FrameDebugger = function($append_id) {
    this.$append_id = $($append_id);
    this._last_prof_total = 0;
    this._num_profs = 0;

    this.add_append_profile = function(delta) {
        this._last_prof_total += delta;
        this._num_profs++;
        console.log('op: ' + delta + ' avg: ' + (this._last_prof_total / this._num_profs));
    }

    function str_to_bytearray(str) {
        var result = [];
        for (i = 0; i < str.length; i++)
            result.push('0x' + str.charCodeAt(i).toString(16));

            return result;
    }

    var toggle_value_format = function () {
        var $this = $(this);
        var value16 = $this.attr('value16');
        var value2 = $this.attr('value2');
        var value10 = $this.attr('value10');
        if ($this.text() == value16)
            $this.text(value2);
        else if ($this.text() == value2)
            $this.text(value10);
        else
            $this.text(value16);
    };

    $toggle_a_template = $('<a/>').attr('href', 'javascript:void(0)');

    this.generate_hex_output = function($append_node, frame, label) {
        var $content = $('<div />').addClass('content');
        $content.hide();


        var $table = $('<table style="font-family: monospace;"><thead><th>byte dump</th><th>ascii</th></thead><tbody></tbody></table>');
        var $body = $('tbody', $table);
        var col_counter = 0;
        // display
        var $ascii_col;
        var $byte_col;

        var assembly = frame.get_assembly();
        var msg_data = assembly.get_data();
        var start = assembly.get_start_pos();
        var end = msg_data.length;
        if (label == "RECV:")
            end = assembly.get_pos();

        for (var i=start; i<end; i++) {


            if (col_counter==0) {
                $byte_col = $('<td style="padding-right: 10px"/>');
                $ascii_col = $('<td style="padding-left:10px"/>');
            }

            var ascii = $('<span />').text(msg_data[i]);
            var byte = msg_data.charCodeAt(i);
            if (!(byte >= 32 && byte <= 176))
                ascii = '.';

            var byte16 = byte.toString(16);
            if (byte16.length != 2)
                byte16 = '0' + byte16

            byte16 = '0x' + byte16;
            var byte2 = byte.toString(2);
            if (byte2.length != 8) {
                var padding = '';
                for (var j = 0; j < 8 - byte2.length; j++)
                    padding += '0';

                byte2 = padding + byte2;
            }


            if(DEBUG_LEVEL >= 3)
                $byte_a = $toggle_a_template.clone().click(toggle_value_format);
            else
                $byte_a = $('<span/>');


            $byte_a.text(byte16 + ' ');

            $byte_a.attr('value10', byte.toString(10));
            $byte_a.attr('value16', byte16);
            $byte_a.attr('value2', byte2);

            $byte_col.append($byte_a);
            $ascii_col.append(ascii);

            col_counter++;

            if (col_counter == 8) {
                $byte_col.append('<span>&nbsp;</span>');
                $ascii_col.append('<span>&nbsp;</span>');
            } else if (col_counter == 16) {
                col_counter = 0;
                var $row = $('<tr />');
                $row.append($byte_col).append($ascii_col);
                $body.append($row);
            }
        }


        if (col_counter != 16) {
            var $row = $('<tr />');
            $row.append($byte_col).append($ascii_col);
            $body.append($row);
        }


        $content.append($table);
        $append_node.append($content);
    };

    this.append_msg = function(label, msg) {
        if (!DEBUG_LEVEL)
            return;

        var start_prof = new Date().getTime();

        var $li = $('<li />');
        var $link = $('<a />').attr('href', 'javascript:void(0)');
        $li.append($link);
        $li.append('<br />');

        var date = new Date()

        var header='';
        header = date.toString() + ' ' + label
        header += ': Class: ' + msg.get_class_name() + ' Message: ' + msg.get_name() + '';

        $link.text(header);

        $link.click(function() {
            var $content = $('.content', $(this).parent());
            $content.slideToggle();
            return false;
        });

        /*
        if (DEBUG_LEVEL > 1)
            this.generate_hex_output($li, frame, label);
        */

        this.$append_id.append($li);
        var $bottom = $('#bottom');
        $bottom[0].scrollIntoView(true);

        var end_prof = new Date().getTime();
        var delta = end_prof - start_prof;
        this.add_append_profile(delta);

    }

}
})();