(function() {
/* Boilerplate
 */
if (!window.WillowChat) {
    Willowchat = {}
}

if (!WillowChat.chrome) {
    WillowChat.chrome = {}
}

if (!WillowChat.chrome.map) {
    WillowChat.chrome.map = {}
}


WillowChat.chrome.map.simple = WillowChat.chrome.SimpleChrome = function(container, opts) {
    /* Set configured height
     */
    container.style.width = opts.width + 'px'
    container.style.height = opts.height + 'px'
    container.style.background = "white";
    var toggles = document.createElement('div')
    toggles.setAttribute('id', 'willowchatToggles')
    var floatToggle = document.createElement('div')
    floatToggle.setAttribute('id', 'willowchatFloat')
    floatToggle.innerHTML = "&uarr;"
    var minToggle = document.createElement('div')
    minToggle.setAttribute('id', 'willowchatMin')
    minToggle.innerHTML = "-"
    floatToggle.setAttribute('style', "float: left;")
    minToggle.setAttribute('style', "float: left;")
    var toggleElements = [ minToggle, floatToggle]
    for (var i = 0; i < 2; ++i) {
        var t = toggleElements[i]
        t.style.width = "20px"
        t.style.height = "20px"
        t.style.textAlign = "center"
        t.style.border = "1px solid black"
        t.style.padding = "2px"
        t.style.color = "white"
        t.style.fontWeight = "bold"
        t.style.background = "#005522"
        t.style.cursor = "pointer"
        t.style.cssFloat = "left"
        t.style.styleFloat = "left"
        t.style.display = "none"
    }
    container.appendChild(toggles)
    toggles.appendChild(floatToggle)
    toggles.appendChild(minToggle)

    /* Should it be floating?
     */
    if (opts.floating) {
        container.style.position = 'absolute';
        container.style.bottom = '0';
        container.style.right = '0';
        minToggle.style.display = "block"
        toggles.style.position = "absolute"
        toggles.style.top = "1px"
        toggles.style.left = "1px"
        if (opts.reposition) {
            container.parentNode.removeChild(container)
            document.body.appendChild(container)

        }
    }
    else {
        var ifr = container.getElementsByTagName('iframe')[0]
        toggles.style.marginBottom="-10px"
        ifr.style.marginTop="10px"
        container.removeChild(ifr)
        container.appendChild(ifr)
//        toggles.style.marginBottom = "-5px";
    }
    if (opts.floatingToggle) {
        floatToggle.style.display = "block"
    }
    toggles.style.border = "1ps solid yellow"
}

})();
