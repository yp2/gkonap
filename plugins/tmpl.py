#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
#       plugins.tmpl
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
try:
    from cdecimal import Decimal, ROUND_DOWN
except ImportError:
    from decimal import Decimal, ROUND_DOWN

class PluginTMPL(ConvertBase):
    def __init__(self):
        super(PluginTMPL, self).__init__()
        
        self.name = "Plugin TMPlayer"
        self.description = "Plugin for TMPlayer format of subtitles"
        self.plugin_subtype = 'tmpl'
        self.re_subs_type = '^\d{1,2}:\d{2}:\d{2}:'
        self.re_decompose_subs = re.compile(r'(\d{1,2}:\d{2}:\d{2}:)')
        self.compose_line = '%s%s\n'
        
    def decompose(self, subtitle_file_path, movie_fps):
        super(PluginTMPL, self).decompose(subtitle_file_path, movie_fps)
        
        self.preDecomposeProcessing()
        
        #podział na na listetime_start time_stop napis
        #będącecj wynikiem podziału na grupy [wyrażenie re z ()]
        #wycinek listy element 0 jest pusty
        _decompose_subs = self.re_decompose_subs.split(self.joined_sub)[1:]
        
        #utworzenie listy zawierającej linie poszczególnych  
        #napisów w postaci listy [time_start, time_stop, napis]
        #[[], [], [], ...]
        #plus konwersja czasu na sekundy z dokładmości do 1000 częsci sekundy
        _decompose_subs_lines = []
        while _decompose_subs:
            
            time_start = self.decomposeTimeConversion(_decompose_subs[0])
            try:
                time_stop = self.decomposeTimeConversion(_decompose_subs[2])
            except IndexError:
                #wychwycenie końca listy, przekazanie listy z pierwszą pozycją
                #określającą co się stało, druga pozycja to czas początku napisu
                time_stop = self.decomposeTimeConversion(['stop', _decompose_subs[0]])
                
            sub_line = _decompose_subs[1]
            line = [time_start, time_stop, sub_line]
            _decompose_subs_lines.append(line)
            _decompose_subs = _decompose_subs[2:]
        
        
        self.decomposed_subtitle = _decompose_subs_lines
        
        #porównienie czasów bardzo nie dokładny format
        #maksymalna róźnica pomiędzy startem a stop w sekundach
        _max_diff_time = 6
        self.postDecomposeTimeProcessing(_max_diff_time)
    
        
        self.postDecomposeProcsessing()
        
    def postDecomposeTimeProcessing(self, max_diff_time):
        """
        Methoda dla bardzo niedokładnych napisów np TMPlayer.
        Porównuje czasy startu i stopu.
        Napisy w formaie listy w liście [[],[],...] 
        
        @max_diff_time - w sekundach
        """
        subs = self.decomposed_subtitle
        subs_out = []
        while subs:
            time_start = subs[0][0]
            time_stop = subs[0][1]
            subs_line = subs[0][2]
            diff_time = time_stop - time_start
            if diff_time > max_diff_time:
                time_stop = time_start + max_diff_time
            subs_out.append([time_start, time_stop, subs_line])
            subs = subs[1:]
        
        self.decomposed_subtitle = subs_out    
    
    def decomposeTimeConversion(self, time, movie_fps=None):
        if type(time) is list:
            #jako czas końcowy dla ostaniego napisu użyjemy jego początku
            #następnie przy zwracaniu dodamy określony czas
            time = time[1]
            #dodajemy do końcowgo czasu
            _plus_t_stop = 2
        else:
            #nic nie dodajmy
            _plus_t_stop = 0
    
        _re_time = re.compile(r"(?P<hour>\d{1,2}):(?P<min>\d{2}):(?P<sec>\d{2}):")
        _re_time = _re_time.match(time)
        _re_time = _re_time.groupdict()
        _t_hour = float(_re_time['hour'])
        _t_min = float(_re_time['min'])
        _t_sec = float(_re_time['sec'])
        conv_time = (_t_hour * 3600) + (_t_min * 60) + _t_sec + _plus_t_stop
        conv_time = Decimal(str(conv_time))
          
        return conv_time.quantize(Decimal('1.000'), rounding=ROUND_DOWN)
        
    def preDecomposeProcessing(self):
        super(PluginTMPL, self).preDecomposeProcessing()
        
    def compose(self, movie_fps):
        super(PluginTMPL, self).compose(movie_fps)
        
        #decopmse to lista w liście - [[], [], ...]
        #wewnętrzne listy oznaczają poszczególne linie
        
        #w tym miejscu jest ostatnia możliwość zmiany czegoś w lini napisów
        #chodzi o metoda subProcessing
        self.subProcesing()
        
        _compose_subs = []
        while self.decomposed_subtitle:
            sub_line = self.decomposed_subtitle[0]
            time_start = self.composeTimeConversion(sub_line[0])
            # czas stop nie istnieje dla tego formatu
            line = sub_line[2]
            
            # '%s%s%s'
            conv_line = self.compose_line % (time_start, line)
            _compose_subs.append(conv_line)
            
            self.decomposed_subtitle = self.decomposed_subtitle[1:]
        
        self.compose_subtitle = _compose_subs
        
    def composeTimeConversion(self, time, movie_fps=None):
        """
        Metdoa do konwersji czasu dla danego formatu 
        wynik w postaci gotowy do wstawienia do szablonu napisu
        @time = czas w sekundach uwaga w formacie Decimal
        @movie_fps = ilość klatek na sekundę
        """
        second = time
        hour = second // (3600)
        second %= 3600
        minute = second // 60
        second %= 60
        
        conv_time = "%02d:%02d:%02d:" % (hour, minute, second)
        return conv_time

if __name__ == "__main__":
    sub_path = '/home/daniel/git/gkonap/test_files/tmpl.txt'
    ct_sub_path = '/home/daniel/git/gkonap/test_files/ct_tmpl.txt'
    movie_fps = 23.976
    plugin = PluginTMPL()
    plugin.decompose(sub_path, movie_fps)
    subs = plugin.decomposed_subtitle
    plugin.decomposed_subtitle = None
    plugin.decomposed_subtitle = subs
    plugin.compose(movie_fps)
    print plugin.compose_subtitle[0]
    plugin.writeComposeSubs(ct_sub_path)
    