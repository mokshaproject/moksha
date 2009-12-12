<div id="${id}">

  <input id="chat_${id}_name" type="text" value="Anonymous" size="10"/>
  <input id="chat_${id}_input" type="text" size="34" name="input"
         onkeypress="moksha.on_enter(event, send_chat_message)">
  <br/>
  <textarea id="chat_${id}" cols="55" rows="25" readonly="true">Welcome to ${topic}</textarea>

  <script type="text/javascript">
      function send_chat_message(){
          var input = $('#chat_${id}_input');
          moksha.send_message('${topic}', {
                  message: input.val() + '\n',
                  name: $('#chat_${id}_name').val()
          });
          input.val("");
      }
      $('#chat_${id}_input').focus();
  </script>

</div>
