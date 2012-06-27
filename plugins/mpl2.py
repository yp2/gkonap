#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
#       plugins.mpl2
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

class PluginMPL2(ConvertBase):
    def __init__(self):
        super(PluginMPL2, self).__init__()
        
        self.name = "Plugin MPL2"
        self.description = "Plugin for MPL2 format of subtitles"
        self.subtype = 'mpl2'
        self.re_subs_type = r'^\[\d*\]'