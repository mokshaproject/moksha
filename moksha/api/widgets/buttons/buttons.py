# This file is part of Moksha.
#
# Moksha is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Moksha is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Moksha.  If not, see <http://www.gnu.org/licenses/>.

"""
:mod:`moksha.api.widgets.buttons` - Fancy Button CSS
====================================================

This module contains a ToscaWidget for the mbButtons
project::

    http://www.open-lab.com/mb.ideas/index.html#mbButtons

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

from tw.api import CSSLink, Link

buttons_css = CSSLink(filename='static/buttons.css',
                      media='all', modname=__name__)
static_images = Link(filename='static/images/ventitre.gif', modname=__name__)
