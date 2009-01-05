var bars = [];
var num_bars = 10;

// Make ten bars that are blue
var init_graph = function(container_name) {

    var container = document.getElementById(container_name);
    for (var i=0; i< num_bars; i++) {
        var bar = document.createElement('div');
        bar.className = "bar";
        bar.style.width = "100px";
        bars.push(bar);
        container.appendChild(bar);
    }
    // some pizazz... one bar gets to be red.
    bars[3].style.backgroundColor = "red";
};

// Change the length of the bars to match given numerical data
var modify_graph = function(bars, payload) {
    var vals = JSON.parse(payload);
    for (var i=0; i<bars.length; i++) {
        var bar = bars[i];
        bar.style.width = vals[i] + "px";
    }
}
