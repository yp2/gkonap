#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
#       plugins.srt
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
import re

class PluginSRT(ConvertBase):
    def __init__(self):
        super(PluginSRT, self).__init__()
        
        self.name = "Plugin SRT"
        self.description = "Plugin for SubRip Format of subtitles"
        self.subtype = 'srt'
        self.re_subs_type = r'^\d{1}$'
        self.re_decompose_subs = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n')
        
    def decompose(self, subtitle_file_path, movie_fps):
        super(PluginSRT, self).decompose(subtitle_file_path, movie_fps)
        
        self.preDecomposeProcessing()
        
        #podział na na listę time_start time_stop napis
        #będącecj wynikiem podziału na grupy [wyrażenie re z ()]
        #wycinek listy element 0 jest pust
        _decompose_subs = self.re_decompose_subs.split(self.joined_sub)[1:]
        
        #utworzenie listy zawierającej linie poszczególnych  
        #napisów w postaci listy [time_start, time_stop, napis]
        #[[], [], [], ...]
        #plus konwersja czasu na sekundy z dokładmości do 1000 częsci sekundy
        _decompose_subs_lines = []
        while _decompose_subs:
            time_start = self.decomposeTimeConversion(_decompose_subs[0])
            time_stop = self.decomposeTimeConversion(_decompose_subs[1])
            sub_line = _decompose_subs[2]
            line = [time_start, time_stop, sub_line]
            _decompose_subs_lines.append(line)
            _decompose_subs = _decompose_subs[3:]
        
        self.decomposed_subtitle = _decompose_subs_lines
        
    def decomposeTimeConversion(self, time):
        _re_time = re.compile('(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2}),(?P<msec>\d{3})')
        _re_time = _re_time.match(time)
        _re_time = _re_time.groupdict()
        _t_hour = float(_re_time['hour'])
        _t_min = float(_re_time['min'])
        _t_sec = float(_re_time['sec'])
        _t_msec = float(_re_time['msec'])/1000
        conv_time = (_t_hour * 3600) + (_t_min * 60) + _t_sec + _t_msec 
        conv_time = round(conv_time, 3)
        return conv_time
    
    def preDecomposeProcessing(self):
        #delete first line in srt type of subs 
        #subs converted to list
        self.subtile_file = list(self.subtile_file)[1:]
        
        super(PluginSRT, self).preDecomposeProcessing()
        
        # subs type specific pre processing
        # remove marks of linies
        self.joined_sub = re.sub(r'\n{2}\d*\n', '', self.joined_sub)
        
