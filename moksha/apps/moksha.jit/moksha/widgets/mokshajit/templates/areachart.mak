<script>	 

var labelType, useGradients, nativeTextSupport, animate;

(function() {
	  var ua = navigator.userAgent,
	      iStuff = ua.match(/iPhone/i) || ua.match(/iPad/i),
	      typeOfCanvas = typeof HTMLCanvasElement,
	      nativeCanvasSupport = (typeOfCanvas == 'object' || typeOfCanvas == 'function'),
	      textSupport = nativeCanvasSupport 
	        && (typeof document.createElement('canvas').getContext('2d').fillText == 'function');
	  //Im setting this based on the fact that ExCanvas provides text support for IE
	  //and that as of today iPhone/iPad current text support is lame
	  labelType = (!nativeCanvasSupport || (textSupport && !iStuff))? 'Native' : 'HTML';
	  nativeTextSupport = labelType == 'Native';
	  useGradients = nativeCanvasSupport;
	  animate = !(iStuff || !nativeCanvasSupport);
})();

var Log = {
    elem: false,
    write: function(text){
        if (!this.elem) 
            this.elem = document.getElementById('log');
        this.elem.innerHTML = text;
        this.elem.style.left = (500 - this.elem.offsetWidth / 2) + 'px';
    }
};

function addEvent(obj, type, fn) {
    if (obj.addEventListener) obj.addEventListener(type, fn, false);
    else obj.attachEvent('on' + type, fn);
};

$(document).ready(function(){
    var areaChart = new $jit.AreaChart({  
		//id of the visualization container  
		injectInto: 'infovis',  
		
		//add animations  
		animate: true,  
		
		//separation offsets  
		offset: 5,  
		labelOffset: 10,  

		//whether to display sums  
		showAggregates: true,  

		//whether to display labels at all  
		showLabels: true,  

		//could also be 'stacked'  
		type: useGradients ? 'stacked:gradient' : 'stacked',  

		//label styling  
		Label: {  
			type: labelType, //can be 'Native' or 'HTML'  
			size: 13,  
			family: 'Arial',  
			color: 'white'  
		},  

		//enable tips  
		Tips: {  
			enable: true,  
			onShow: function(tip, elem) {  
				tip.innerHTML = "<b>" + elem.name + "</b>: " + elem.value;  
			}  
		},  

		//add left and right click handlers  
		filterOnClick: true,  
		restoreOnRightClick:true  
	});  
    //load JSON data.  
    $.getJSON('${query}', function(json) {
        areaChart.loadJSON(json.chart); 
    });
});
</script>

<div id="container">

    <div id="left-container">
        <div class="text">
            <h4>${title}</h4> 
            ${description}
        </div>

        <div id="id-list"></div>

    </div>

    <div id="center-container">
        <div id="infovis"></div>
    </div>

    <div id="right-container">
        <div id="inner-details"></div>
    </div>

    <div id="log"></div>

</div>
