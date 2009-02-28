/*
 *         developed by Matteo Bicocchi on JQuery
 *        © 2002-2009 Open Lab srl, Matteo Bicocchi
 *			    www.open-lab.com - info@open-lab.com
 *       	version 1.5.3
 *       	tested on: 	Explorer and FireFox for PC
 *                  		FireFox and Safari for Mac Os X
 *                  		FireFox for Linux
 *         GPL (GPL-LICENSE.txt) licenses.
 */
//document.oncontextmenu = function() { return false };

// to get the element that is fireing a contextMenu event you have $.mbMenu.lastContextMenuEl that returns an object.
(function($) {
	$.mbMenu = {
		actualMenuOpener:false,
		options: {
			template:"yourMenuVoiceTemplate",// the url that returns the menu voices via ajax. the data passed in the request is the "menu" attribute value as "menuId"
			additionalData:"",
			menuSelector:".menuContainer",
			menuWidth:150,
			openOnRight:false,
			iconPath:"ico/",
			hasImages:true,
			fadeInTime:100,
			fadeOuTime:100,
			menuTop:0,
			menuLeft:0,
			submenuTop:0,
			submenuLeft:4,
			opacity:1,
			shadow:false,
			shadowColor:"black",
			openOnClick:true,
			closeOnMouseOut:false,
			closeAfter:500,
			minZindex:"auto", // or number
			shadowOpacity:.2,
			onContextualMenu:function(o,e){}
		},
		buildMenu : function (options){
			return this.each (function ()
			{
				var thisMenu =this;
				thisMenu.id = !this.id ? "menu_"+Math.floor (Math.random () * 1000): this.id;
				this.options = {};

				$.extend (this.options, $.mbMenu.options);
				$.extend (this.options, options);

				$(".menu").hide();
				thisMenu.clicked = false;
				thisMenu.rootMenu=false;
				thisMenu.clearClicked=false;
				thisMenu.actualOpenedMenu=false;
				thisMenu.menuvoice=false;
				var root=$(this);
				var openOnClick=this.options.openOnClick;
				var closeOnMouseOut=this.options.closeOnMouseOut;

				//build roots
				$(root).each(function(){
					thisMenu.menuvoice=$(this).find("[menu]");
					$(thisMenu.menuvoice).each(function(){
						$(this).addClass("rootVoice");
						$(this).attr("nowrap","nowrap");
					});
					var action= openOnClick?"click":"mouseover";
					$(thisMenu.menuvoice).bind(action,function(){
						if (!$(this).attr("isOpen")){
							$(this).buildMbMenu(thisMenu,$(this).attr("menu"));
						}
						$(this).attr("isOpen","true");

						//empty
						if($(this).attr("menu")=="empty"){
							if(thisMenu.actualOpenedMenu){
								$(thisMenu.actualOpenedMenu).removeClass("selected");
								thisMenu.clicked=true;
								$(this).removeAttr("isOpen");
								clearTimeout(thisMenu.clearClicked);
							}
							$(this).removeMbMenu(thisMenu);
						}

						return false;
					});

					var mouseOver=$.browser.msie?"mouseenter":"mouseover";
					var mouseOut=$.browser.msie?"mouseleave":"mouseout";
					$(thisMenu.menuvoice).bind(mouseOver,function(){
						if (closeOnMouseOut) clearTimeout($.mbMenu.deleteOnMouseOut);
						if (!openOnClick) $(thisMenu).find(".selected").removeClass("selected");
						if(thisMenu.actualOpenedMenu){ $(thisMenu.actualOpenedMenu).removeClass("selected");}
						$(this).addClass("selected");
						if(thisMenu.clicked && !$(this).attr("isOpen")){
							clearTimeout(thisMenu.clearClicked);
							$(this).buildMbMenu(thisMenu,$(this).attr("menu"));
						}
					})
					$(thisMenu.menuvoice).bind(mouseOut,function(){
						if(!thisMenu.clicked)
							$(this).removeClass("selected");
						$(document).bind("click",function(){
							$(this).removeMbMenu(thisMenu);
						})
					})
				})
			})
		},
		buildContextualMenu :  function (options){
			return this.each (function ()
			{
				var thisMenu = this;
				thisMenu.options = {};
				$.extend (thisMenu.options, $.mbMenu.options);
				$.extend (thisMenu.options, options);
				$(".menu").hide();
				thisMenu.clicked = false;
				thisMenu.rootMenu=false;
				thisMenu.clearClicked=false;
				thisMenu.actualOpenedMenu=false;
				thisMenu.menuvoice=false;
				var cMenuEls= $("[cMenu]");
				$(cMenuEls).each(function(){
					$(this).css("-khtml-user-select","none");
					var cm=this;
					cm.id = !cm.id ? "menu_"+Math.floor (Math.random () * 100): cm.id;
					$(cm).css({cursor:"default"});
					$(cm).bind("contextmenu","mousedown",function(event){
						$(this).blur();
						if (event.which==3){
							event.preventDefault();
							event.stopPropagation();
							event.cancelBubble=true;

							//add custom behavior to contextMenuEvent passing the el and the event
							//you can for example store to global var the obj that is fireing the event
							//mbActualContextualMenuObj=cm;
							$.mbMenu.lastContextMenuEl=cm;
							thisMenu.options.onContextualMenu(this,event);

							if ($.mbMenu.options.actualMenuOpener) {
								$(thisMenu).removeMbMenu($.mbMenu.options.actualMenuOpener);
							}
							$(this).buildMbMenu(thisMenu,$(this).attr("cMenu"),"cm",event);
							$(this).attr("isOpen","true");
						}
					})
				})
			})
		}
	}
	$.fn.extend({
		buildMbMenu: function(op,m,type,e){
			var msie6=$.browser.msie && $.browser.version=="6.0";
			var mouseOver=$.browser.msie?"mouseenter":"mouseover";
			var mouseOut=$.browser.msie?"mouseleave":"mouseout";
			$().bind("click",function(){$(document).removeMbMenu(op)})
			if (e) {
				this.mouseX=$(this).getMouseX(e);
				this.mouseY=$(this).getMouseY(e);
			}

			if ($.mbMenu.options.actualMenuOpener && $.mbMenu.options.actualMenuOpener!=op)
				$(op).removeMbMenu($.mbMenu.options.actualMenuOpener);
			$.mbMenu.options.actualMenuOpener=op;
			if(!type || type=="cm")	{
				if (op.rootMenu) {
					$(op.rootMenu).remove();
					$(op.actualOpenedMenu).removeAttr("isOpen")
				}
				op.clicked=true;
				op.actualOpenedMenu=this;
				$(op.actualOpenedMenu).attr("isOpen","true")
				$(op.actualOpenedMenu).addClass("selected");
			}
			var opener=this;
			var where=(!type|| type=="cm")?$(document.body):$(this).parent().parent();

			//empty
			if($(this).attr("menu")=="empty"){
				return;
			}

			var menuClass= op.options.menuSelector.replace(".","")
			where.append("<div class='menuDiv'><div class='"+menuClass+"' style='display:table'></div></div>");
			this.menu  = where.find(".menuDiv");
			if (op.options.minZindex!="auto"){
				$(this.menu).css({zIndex:op.options.minZindex++});
			}else{
				$(this.menu).mbBringToFront();
			}
			this.menuContainer  = $(this.menu).find(op.options.menuSelector);
			$(this.menuContainer).bind(mouseOver,function(){
				$(opener).addClass("selected");
			})
			$(this.menuContainer).css({
				position:"absolute",
				opacity:op.options.opacity
			});
			if (!$("#"+m).html()){
				$.ajax({
					type: "POST",
					url: op.options.template,
					cache: false,
					async: false,
					data:"menuId="+m+(op.options.additionalData!=""?"&"+op.options.additionalData:""),
					success: function(html){
						$("body").after(html);
						$("#"+m).hide();
					}
				});
			}
			$(this.menuContainer).hide();
			this.voices= $("#"+m).find("a").clone();

			if (op.options.shadow) {
				var shadow = $("<div class='menuShadow'></div>").hide();
				if(msie6)
					shadow = $("<iframe class='menuShadow'></iframe>").hide();
			}

			// build each voices of the menu
			$(this.voices).each(function(i){

				var voice=this;
				var imgPlace="";

				var isText=$(voice).attr("rel")=="text";
				var isTitle=$(voice).attr("rel")=="title";
				var isDisabled=$(voice).is("[disabled]");
				var isSeparator=$(voice).attr("rel")=="separator";

				if (op.options.hasImages && !isText){

					var imgPath=$(voice).attr("img")?$(voice).attr("img"):"blank.gif";
					imgPath=(imgPath.length>3 && imgPath.indexOf(".")>-1)?"<img class='imgLine' src='"+op.options.iconPath+imgPath+"'>":imgPath;
					imgPlace="<td class='img'>"+imgPath+"</td>"
				}
				var line="<table id='"+m+"_"+i+"' class='line"+(isTitle?" title":"")+"' cellspacing='0' cellpadding='0' border='0' style='width:100%; display:table' width='100%'><tr>"+imgPlace+"<td class='voice' nowrap></td></tr></table>";
				if(isSeparator)
					line="<div class='separator' style='width:100%; display:inline-block'><img src='"+op.options.iconPath+"blank.gif' width='1' height='1'></div>"
				if(isText)
					line="<div style='width:100%; display:table' class='line' id='"+m+"_"+i+"'><div class='voice'></div></div>";

				$(opener.menuContainer).append(line);

				if(!isSeparator){
					$(opener.menuContainer).find("#"+m+"_"+i).find(".voice").append(this);
					if($(this).attr("menu")){
						$(opener.menuContainer).find("#"+m+"_"+i).find(".voice a").wrap("<div class='menuArrow'></div>");
						$(opener.menuContainer).find("#"+m+"_"+i).find(".menuArrow").addClass("subMenuOpener");
						$(opener.menuContainer).find("#"+m+"_"+i).css({cursor:"default"})
						this.isOpener=true;
					}
					if(isText){
						$(opener.menuContainer).find("#"+m+"_"+i).find(".voice").addClass("textBox");
						this.isOpener=true;
					}
					if(isDisabled){
						$(opener.menuContainer).find("#"+m+"_"+i)
							.addClass("disabled")
							.css({cursor:"default"})
					}

					if(!(isText || isTitle || isDisabled)){
						$(opener.menuContainer)
							.find("#"+m+"_"+i)
							.css({cursor:"pointer"})
							.bind("mouseover",function(event){
							clearTimeout($.mbMenu.deleteOnMouseOut);
							$(this).addClass("selected");
							if(opener.menuContainer.actualSubmenu && !$(voice).attr("menu")){
								$(opener.menu).find(".menuDiv").remove();
								$(opener.menuContainer.actualSubmenu).removeClass("selected");
								opener.menuContainer.actualSubmenu=false;
								//return false;
							}
							if ($(voice).attr("menu")){

								if(opener.menuContainer.actualSubmenu && opener.menuContainer.actualSubmenu!=this){
									$(opener.menu).find(".menuDiv").remove();
									$(opener.menuContainer.actualSubmenu).removeClass("selected");
									opener.menuContainer.actualSubmenu=false;
								}
								if (!$(voice).attr("action")) $(opener.menuContainer).find("#"+m+"_"+i).css("cursor","default")
								if (!opener.menuContainer.actualSubmenu || opener.menuContainer.actualSubmenu!=this){
									$(opener.menu).find(".menuDiv").remove();

									opener.menuContainer.actualSubmenu=false;
									$(this).buildMbMenu(op,$(voice).attr("menu"),"sm",event);
									opener.menuContainer.actualSubmenu=this;
								}
								$(this).attr("isOpen","true")
								return false;
							}
						})
						$(opener.menuContainer).find("#"+m+"_"+i).bind(mouseOut,function(){
							$(this).removeClass("selected");
						})
					}
					if(isDisabled || isTitle){
						$(this).removeAttr("href");
						$(opener.menuContainer).find("#"+m+"_"+i).bind(mouseOver,function(){
							$(document).unbind("click");
							if(opener.menuContainer.actualSubmenu){
								$(opener.menu).find(".menuDiv").remove();
								opener.menuContainer.actualSubmenu=false;
							}
						}).css("cursor","default")
					}
					$(opener.menuContainer).find("#"+m+"_"+i).bind("click",function(){
						if (($(voice).attr("action") || $(voice).attr("href")) && !isDisabled){
							var target=$(voice).attr("target")?$(voice).attr("target"):"_self";
							if ($(voice).attr("href") && $(voice).attr("href").indexOf("javascript:")>-1){
								$(voice).attr("action",$(voice).attr("href").replace("javascript:",""));
								$(voice).removeAttr("href");
							}
							var link=$(voice).attr("action")?$(voice).attr("action"):"window.open('"+$(voice).attr("href")+"', '"+target+"')";
							$(voice).removeAttr("href");
							eval(link);
							$(this).removeMbMenu(op);
						}else if($(voice).attr("menu"))
							return false;
					})
				}
			})

			// Close on Mouseout

			var closeOnMouseOut=$(op)[0].options.closeOnMouseOut;
			if (closeOnMouseOut){
				$(opener.menuContainer).bind("mouseenter",function(){
					clearTimeout($.mbMenu.deleteOnMouseOut);
				})
				$(opener.menuContainer).bind("mouseleave",function(){
					var menuToRemove=$.mbMenu.options.actualMenuOpener;
					$.mbMenu.deleteOnMouseOut= setTimeout(function(){$(this).removeMbMenu(menuToRemove)},$(op)[0].options.closeAfter);
				})
			}


			//positioning opened
			var t=0,l=0
			$(this.menuContainer).css({
				width:op.options.menuWidth
			})
			if ($.browser.msie) $(this.menuContainer).css("width",$(this.menuContainer).width()+2);


			switch(type){
				case "sm":
					t=$(this).position().top+op.options.submenuTop;

					l=$(this).position().left+$(this).width()-op.options.submenuLeft;
					break;
				case "cm":
					t=this.mouseY-5;
					l=this.mouseX-5;
					break;
				default:
					if (op.options.openOnRight){
						t=$(this).offset().top-($.browser.msie?2:0)+op.options.menuTop;
						l=$(this).offset().left+$(this).outerWidth()-op.options.menuLeft-($.browser.msie?2:0);
					}else{
						t=$(this).offset().top+$(this).outerHeight()-(!$.browser.mozilla?2:0)+op.options.menuTop;
						l=$(this).offset().left+op.options.menuLeft;
					}
					break;
			}

			$(this.menu).css({
				position:"absolute",
				top:t,
				left:l
			})

			if (!type || type=="cm") op.rootMenu=this.menu;
			$(this.menuContainer).bind(mouseOut,function(){
				$(document).bind("click",function(){$(document).removeMbMenu(op)})
			})

			if (op.options.fadeInTime>0) $(this.menuContainer).fadeIn(op.options.fadeInTime);
			else $(this.menuContainer).show();

			if (op.options.shadow) {
				$(this.menu).prepend(shadow)
				shadow.css({
					width:$(this.menuContainer).outerWidth(),
					height:$(this.menuContainer).outerHeight()-1,
					position:'absolute',
					backgroundColor:op.options.shadowColor,
					border:0,
					opacity:op.options.shadowOpacity
				}).show();
			}

			var wh=$(window).height();
			var ww=$(window).width();
			var mh=$(this.menuContainer).outerHeight();
			var mw=shadow?shadow.outerWidth():$(this.menuContainer).outerWidth();

			var actualX=$(where.find(".menuDiv:first")).offset().left;
			var actualY=$(where.find(".menuDiv:first")).offset().top;
			switch(type){
				case "sm":
					if ((actualX+mw)>= ww){
						l-=((op.options.menuWidth*2)-(op.options.submenuLeft*2))
					}
					break;
				case "cm":
					if ((actualX+(op.options.menuWidth*1.5))>= ww){
						l-=((op.options.menuWidth*2)-(op.options.submenuLeft))
					}
					break;
				default:
					if ((actualX+mw)>= ww){
						l-=($(this.menuContainer).offset().left+mw)-ww;
					}
					break;
			}
			if ((actualY+mh)>= wh-10){
				t-=((actualY+mh)-wh)+30;
			}

			$(this.menu).css({
				top:t,
				left:l
			})
		},
		removeMbMenu: function(op){
			if(!op)op=$.mbMenu.options.actualMenuOpener;
			if (op.rootMenu) {
				$(op.actualOpenedMenu)
					.removeAttr("isOpen")
					.removeClass("selected")
				$(op.rootMenu).fadeOut($.mbMenu.options.fadeOuTime,function(){$(this).remove()});
				op.rootMenu=false;
				op.clicked=false
				$(document).unbind("click");
			}
		},

		//mouse  Position
		getMouseX : function (e){
			var mouseX;
			if ($.browser.msie)mouseX = event.clientX + document.body.scrollLeft;
			else mouseX = e.pageX;
			if (mouseX < 0) mouseX = 0;
			return mouseX;
		},
		getMouseY : function (e){
			var mouseY;
			if ($.browser.msie)	mouseY = event.clientY + document.body.scrollTop;
			else mouseY = e.pageY;
			if (mouseY < 0)	mouseY = 0;
			return mouseY;
		},
		//get max z-inedex of the page
		mbBringToFront: function(){
			var zi=10;
			$('*').each(function() {
				if($(this).css("position")=="absolute"){
					var cur = parseInt($(this).css('zIndex'));
					zi = cur > zi ? parseInt($(this).css('zIndex')) : zi;
				}
			});

			$(this).css('zIndex',zi+=10);
		}

	})
	$.fn.buildMenu = $.mbMenu.buildMenu;
	$.fn.buildContextualMenu = $.mbMenu.buildContextualMenu;
})(jQuery);