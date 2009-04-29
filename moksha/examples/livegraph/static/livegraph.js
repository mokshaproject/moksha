// This file is part of Moksha.
// Copyright (C) 2008-2009  Red Hat, Inc.
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
// 
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
