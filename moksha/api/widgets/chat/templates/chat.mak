<script>
  TCPSocket = Orbited.TCPSocket
  document.domain = document.domain;
</script>

<div id="popup">
<div id="popupOuter">
  <div id="popupMiddle">
    <div id="popupContent">
      <p>Greeting</p>
      <label for="nickname">Nickname:</label>
      <input type="text" id="nickname" maxlength="16" style="width: 10em;" value="" />
    </div>
  </div>
</div>
</div>

  <div id="absorbClicks"></div>
  <div id="presenceToggle">
    &rarr;
  </div>
  <div id="presence">
   <div id="presenceTitle">Presence</div>
   <div id="presenceList">
   </div>
  </div>
  <div id="history">
  </div>
  <div id="inputBar">
   <textarea id="chatboxInput"></textarea>
  </div>
