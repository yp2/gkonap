#!/usr/bin/env python
#-*- coding: utf-8 -*-

#       plugins.__init__
#       
#       Copyright 2012 Daniel Dereziński <daniel.derezinski@gmial.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA

from gkcore.convert import ConvertBase
from gkcore.subsdwn import SubsDownloadBase
from gkcore.core import pluginLoad, pluginInstance
import os

PLUGIN_DIR = [os.path.dirname(__file__)]    #katalog bazowy dla pluginów
PLUGINS_CONVERT = None
PLUGINS_SUBS_DOWN = None

_plugins_convert = pluginLoad(PLUGIN_DIR, ConvertBase)
PLUGINS_CONVERT = pluginInstance(_plugins_convert)

_plugins_subs_down = pluginLoad(PLUGIN_DIR, SubsDownloadBase)
PLUGINS_SUBS_DOWN = pluginInstance(_plugins_subs_down)