/*
 *         developed by Matteo Bicocchi on JQuery
 *         © 2002-2008 Open Lab srl, Matteo Bicocchi
 *			    www.open-lab.com - info@open-lab.com
 *       	version 1.0
 *       	tested on: 	Explorer and FireFox for PC
 *                  		FireFox and Safari for Mac Os X
 *                  		FireFox for Linux
 *         GPL (GPL-LICENSE.txt) licenses.
 */


var msie6=$.browser.msie && $.browser.version=="6.0";
var zi=100;
jQuery.fn.buildContainers = function (){
    return this.each (function ()
    {
        var container=$(this);
        container.find(".containerTable:first").css("width","100%");
        container.find(".c:first").wrapInner("<div class='containerBody'style='display:block'></div>");
        container.find(".containerBody:first").wrapInner("<div class='spacer'></div>");
        container.find(".n:first").attr("unselectable","on");
        var icon=container.attr("icon")?container.attr("icon"):"";
        var buttons=container.attr("buttons")?container.attr("buttons"):"";
        container.setIcon(icon);
        container.setButtons(buttons);
        if (msie6 && container.css("height")=="auto") container.find(".containerBody:first").hide();
        container.find(".containerBody:first", ".c:first").css("height",container.outerHeight()-container.find(".n:first").outerHeight()-container.find(".s:first").outerHeight());
        if (msie6 && container.css("height")=="auto") container.find(".containerBody:first").show();
        if (container.hasClass("draggable")){
            container.css({position:"absolute"});
            container.css({zIndex:zi++});
            container.draggable({handle:".n:first",cancel:".c",delay:0, containment:"document"});
            container.mousedown(function(){
                $(this).css({zIndex:zi++});
            }
                    );
        }
        if (container.hasClass("resizable")){
            container.containerResize();
        }
    });
}
jQuery.fn.containerResize = function (){
    $(this).resizable({
        handles:$(this).hasClass("draggable") ? "":"s,e",
        minWidth: 150,
        minHeight: 150,
        helper: "proxy",
        transparent: !$.browser.msie,
        autoHide: !msie6,
        stop:function(e,o){
            var resCont=msie6 ?o.helper:$(this);
            this.elHeight= resCont.outerHeight()-$(this).find(".n:first").outerHeight()-$(this).find(".s:first").outerHeight();
            $(this).find(".containerBody:first",".c:first").css({height: this.elHeight});
        }
    });
}
jQuery.fn.setIcon = function (icon){
    if (icon !="" ){
        $(this).find(".no:first").append("<img class='icon' src='/toscawidgets/resources/moksha.widgets.container.container/static/css/elements/"+icon+"' style='position:absolute'>");
    }else{
        $(this).find(".n:first").css({paddingLeft:"0"});
    }
}
jQuery.fn.setButtons = function (buttons){
    var container=$(this);
    if (buttons !=""){
        var btn=buttons.split(",");
        $(this).find(".ne:first").append("<div class='buttonBar' style='position:absolute'></div>");
        for (var i in btn){
            if (btn[i]=="c"){
                $(this).find(".buttonBar:first").append("<img src='/toscawidgets/resources/moksha.widgets.container.container/static/css/elements/close.png' class='close'>");
                $(this).find(".close:first").bind("click",function(){container.fadeOut(200)});
            }
            if (btn[i]=="m"){
                $(this).find(".n:first").attr("unselectable","on");
                $(this).find(".buttonBar:first").append("<img src='/toscawidgets/resources/moksha.widgets.container.container/static/css/elements/min.png' class='minimizeContainer'>");
                $(this).find(".minimizeContainer:first").bind("click",function(){container.minimize()});
                $(this).find(".n:first").bind("dblclick",function(){container.minimize()});
            }
            if (btn[i]=="p"){
                $(this).find(".buttonBar:first").append("<img src='/toscawidgets/resources/moksha.widgets.container.container/static/css/elements/print.png' class='printContainer'>");
                $(this).find(".printContainer:first").bind("click",function(){});
            }
            if (btn[i]=="i"){
                $(this).find(".buttonBar:first").append("<img src='/toscawidgets/resources/moksha.widgets.container.container/static/css/elements/iconize.png' class='iconizeContainer'>");
                $(this).find(".iconizeContainer:first").bind("click",function(){container.iconize()});
            }
        }
        var fadeOnClose=$.browser.mozilla || $.browser.safari;
        $(this).find(".buttonBar:first img").css({opacity:.5, cursor:"pointer"}).mouseover(function(){if (fadeOnClose)$(this).fadeTo(200,1)}).mouseout(function(){if (fadeOnClose)$(this).fadeTo(200,.5)});
    }
}
jQuery.fn.minimize = function (){
    var container=$(this);
    if (!this.minimized){
        this.w = container.width();
        this.h = container.height();
        container.find(".containerTable:first").css("width","100%");
        container.find(".middle:first").fadeOut("fast",function(){container.css("height","")});
        this.minimized=true;
        container.find(".minimizeContainer:first").attr("src","/toscawidgets/resources/moksha.widgets.container.container/static/css/elements/max.png");
        container.resizable("destroy");
    }else{
        container.find(".middle:first").fadeIn("slow",function(){container.css("height",container.find(".containerTable:first").height())});
        if (container.hasClass("resizable")) container.containerResize();
        this.minimized=false;
        container.find(".minimizeContainer:first").attr("src","/toscawidgets/resources/moksha.widgets.container.container/static/css/elements/min.png");
    }
}
jQuery.fn.iconize = function (){
    return this.each (function ()
    {
        var container=$(this);
        container.attr("w",container.width());
        container.attr("h",container.height());
        container.attr("t",container.css("top"));
        container.attr("l",container.css("left"));
        container.resizable("destroy");
        if (!$.browser.msie) {
            container.find(".containerTable:first").fadeOut("fast");
            container.animate({ height:"32px", width:"32px",left:0},200);
        }else{
            container.find(".containerTable:first").hide();
            container.css({ height:"32px", width:"32px",left:0});
        }
        container.append("<img src='/toscawidgets/resources/moksha.widgets.container.container/static/css/elements/"+(container.attr("icon")?container.attr("icon"):"restore.png")+"' class='restoreContainer'>");
        container.find(".restoreContainer:first").bind("click",function(){
            if (!$.browser.msie) {
                container.find(".containerTable:first").fadeIn("fast");
                container.animate({height:container.attr("h"), width:container.attr("w"),left:container.attr("l")},200);
            } else {
                container.find(".containerTable:first").show();
                container.css({height:container.attr("h"), width:container.attr("w"),left:container.attr("l")});
            }
            container.find(".restoreContainer:first").remove();
        });
    });
}
