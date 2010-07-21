<body onload="init();">
<script>
var labelType, useGradients, nativeTextSupport, animate;

(function() {
  var ua = navigator.userAgent,
      iStuff = ua.match(/iPhone/i) || ua.match(/iPad/i),
      typeOfCanvas = typeof HTMLCanvasElement,
      nativeCanvasSupport = (typeOfCanvas == 'object' || typeOfCanvas == 'function'),
      textSupport = nativeCanvasSupport 
        && (typeof document.createElement('canvas').getContext('2d').fillText == 'function');
  //I'm setting this based on the fact that ExCanvas provides text support for IE
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


function init(){

    //Implement a node rendering function called 'nodeline' that plots a straight line
    //when contracting or expanding a subtree.
    $jit.ST.Plot.NodeTypes.implement({
        'nodeline': {
          'render': function(node, canvas, animating) {
                if(animating === 'expand' || animating === 'contract') {
                  var pos = node.pos.getc(true), nconfig = this.node, data = node.data;
                  var width  = nconfig.width, height = nconfig.height;
                  var algnPos = this.getAlignedPos(pos, width, height);
                  var ctx = canvas.getCtx(), ort = this.config.orientation;
                  ctx.beginPath();
                  if(ort == 'left' || ort == 'right') {
                      ctx.moveTo(algnPos.x, algnPos.y + height / 2);
                      ctx.lineTo(algnPos.x + width, algnPos.y + height / 2);
                  } else {
                      ctx.moveTo(algnPos.x + width / 2, algnPos.y);
                      ctx.lineTo(algnPos.x + width / 2, algnPos.y + height);
                  }
                  ctx.stroke();
              } 
          }
        }

    });

    //init Spacetree
    //Create a new ST instance
    var st = new $jit.ST({
        'injectInto': 'infovis',
        //set duration for the animation
        duration: 800,
        //set animation transition type
        transition: $jit.Trans.Quart.easeInOut,
        //set distance between node and its children
        levelDistance: 75,
        //set max levels to show. Useful when used with
        //the request method for requesting trees of specific depth
        levelsToShow: 2,
        //set node and edge styles
        //set overridable=true for styling individual
        //nodes or edges
        Node: {
            height: 50,
            width: 90,
            //use a custom
            //node rendering function
            type: 'nodeline',
            color:'#23A4FF',
            lineWidth: 2,
            align:"center",
            overridable: true
        },

        Edge: {
            type: 'bezier',
            lineWidth: 2,
            color:'#23A4FF',
            overridable: true
        },

        //Add a request method for requesting on-demand json trees. 
        //This method gets called when a node
        //is clicked and its subtree has a smaller depth
        //than the one specified by the levelsToShow parameter.
        //In that case a subtree is requested and is added to the dataset.
        //This method is asynchronous, so you can make an Ajax request for that
        //subtree and then handle it to the onComplete callback.
        //Here we just use a client-side tree generator (the getTree function).
        request: function(nodeId, level, onComplete) {

          $.getJSON('/tree/entities_tree', {root: nodeId, levels: level},
                function(data) {
                    if ( data.tree.data.polygrid != undefined ){
                        $('body').append($('<div/>').load('/widgets/polygrid?model=' + data.tree.name + '&chrome=True'));
                    }
                    onComplete.onComplete(nodeId, data.tree);
                });
        },

        onBeforeCompute: function(node){
            Log.write("Loading " + node.name);
        },

        onAfterCompute: function(){
            Log.write("");
        },

        //This method is called on DOM label creation.
        //Use this method to add event handlers and styles to
        //your node.
        onCreateLabel: function(label, node){
            label.id = node.id;
            label.innerHTML = node.name;
            label.onclick = function(){
                st.onClick(node.id);
            };
            //set label styles
            var style = label.style;
            style.width = 100 + 'px';
            style.height = 17 + 'px';
            style.cursor = 'pointer';
            style.color = '#fff';
            //style.backgroundColor = '#1a1a1a';
            style.fontSize = '0.8em';
            style.textAlign= 'center';
            style.textDecoration = 'underline';
            style.paddingTop = '3px';
        },

        //This method is called right before plotting
        //a node. It's useful for changing an individual node
        //style properties before plotting it.
        //The data properties prefixed with a dollar
        //sign will override the global node style properties.
        onBeforePlotNode: function(node){
            //add some color to the nodes in the path between the
            //root node and the selected node.
            if (node.selected) {
                node.data.$color = "#ff7";
            }
            else {
                delete node.data.$color;
            }
        },

        //This method is called right before plotting
        //an edge. It's useful for changing an individual edge
        //style properties before plotting it.
        //Edge data proprties prefixed with a dollar sign will
        //override the Edge global style properties.
        onBeforePlotLine: function(adj){
            if (adj.nodeFrom.selected && adj.nodeTo.selected) {
                adj.data.$color = "#eed";
                adj.data.$lineWidth = 3;
            }
            else {
                delete adj.data.$color;
                delete adj.data.$lineWidth;
            }
        }
    });

    //load json data
    $.getJSON('/tree/entities_tree', {root: '1', levels: 1},
          function(data) {
              st.loadJSON(data.tree);
              //compute node positions and layout
              st.compute();
              //emulate a click on the root node.
              st.onClick(st.root);
              //end
              });

    //Add event handlers to switch spacetree orientation.
   function get(id) {
      return document.getElementById(id);  
    };

    var top = get('r-top'), 
    left = get('r-left'), 
    bottom = get('r-bottom'), 
    right = get('r-right');

    function changeHandler() {
        if(this.checked) {
            top.disabled = bottom.disabled = right.disabled = left.disabled = true;
            st.switchPosition(this.value, "animate", {
                onComplete: function(){
                    top.disabled = bottom.disabled = right.disabled = left.disabled = false;
                }
            });
        }
    };
    
    top.onchange = left.onchange = bottom.onchange = right.onchange = changeHandler;
    //end

}
</script>

<div id="container">
##    <div id="left-container">
##
##        <div class="text">
##            <h4>
##            CIVX SpaceTree
##            </h4>
##            This boat is real.
##        </div>
##
##        <div id="id-list"></div>
##
##    </div>

    <div id="center-container">
        <div id="infovis"></div>
    </div>

##    <div id="right-container">
##
##    <h4>Change Tree Orientation</h4>
##    <table>
##        <tr>
##            <td>
##                <label for="r-left">left </label>
##            </td>
##            <td>
##                <input type="radio" id="r-left" name="orientation" checked="checked" value="left" />
##            </td>
##        </tr>
##        <tr>
##             <td>
##                <label for="r-top">top </label>
##             </td>
##             <td>
##                <input type="radio" id="r-top" name="orientation" value="top" />
##             </td>
##        <tr>
##             <td>
##                <label for="r-bottom">bottom </label>
##              </td>
##              <td>
##                <input type="radio" id="r-bottom" name="orientation" value="bottom" />
##              </td>
##        </tr>
##        <tr>
##              <td>
##                <label for="r-right">right </label>
##              </td> 
##              <td> 
##               <input type="radio" id="r-right" name="orientation" value="right" />
##              </td>
##        </tr>
##    </table>
##
##    </div>

    <div id="log"></div>
</div>
<div id="details">Node details:</div>
</body>
</html>
