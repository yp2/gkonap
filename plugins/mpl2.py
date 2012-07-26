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
import re
try:
    from cdecimal import Decimal, ROUND_DOWN
except ImportError:
    from decimal import Decimal, ROUND_DOWN

class PluginMPL2(ConvertBase):
    def __init__(self):
        super(PluginMPL2, self).__init__()
        
        self.name = "Plugin MPL2"
        self.description = "Plugin for MPL2 format of subtitles"
        self.plugin_subtype = 'mpl2'
        self.re_subs_type = r'^\[\d*\]'
        self.re_decompose_subs = re.compile(r'\[(\d*)\]\[(\d*)\]')
        self.compose_line = '%s%s%s\n'
        
    def decompose(self, subtitle_file_path, movie_fps):
        super(PluginMPL2, self).decompose(subtitle_file_path, movie_fps)
        
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
            time_stop = self.decomposeTimeConversion(_decompose_subs[1])
            sub_line = _decompose_subs[2]
            line = [time_start, time_stop, sub_line]
            _decompose_subs_lines.append(line)
            _decompose_subs = _decompose_subs[3:]
        
        self.decomposed_subtitle = _decompose_subs_lines
        
        self.postDecomposeProcsessing()
    
    def decomposeTimeConversion(self, time):
        #format czasowy w postaci [234] gdzie 23 to sec a 4 do dziesiąte części sek.
        conv_time = float(time)/10
        conv_time = Decimal(str(conv_time))
        return conv_time.quantize(Decimal('1.000'), rounding=ROUND_DOWN,)
    
    def preDecomposeProcessing(self):
        super(PluginMPL2, self).preDecomposeProcessing()
        
    def compose(self, movie_fps):
        super(PluginMPL2, self).compose(movie_fps)
        
        #decopmse to lista w liście - [[], [], ...]
        #wewnętrzne listy oznaczają poszczególne linie
        
        #w tym miejscu jest ostatnia możliwość zmiany czegoś w lini napisów
        #chodzi o metoda subProcessing
        self.subProcesing()
        
        _compose_subs = []
        while self.decomposed_subtitle:
            sub_line = self.decomposed_subtitle[0]
            time_start = self.composeTimeConversion(sub_line[0])
            time_stop = self.composeTimeConversion(sub_line[1])
            line = sub_line[2]
            
            # '%s%s%s'
            conv_line = self.compose_line % (time_start, time_stop, line)
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
        
        conv_time = time * Decimal('10')
        conv_time = '[%d]' % conv_time.quantize(Decimal('1'))
        return conv_time
        
        
        
        
if __name__ == "__main__":
    sub_path = '/home/daniel/git/gkonap/test_files/mpl2.txt'
    ct_sub_path = '/home/daniel/git/gkonap/test_files/ct_mpl2.txt'
    movie_fps = 23.976
    plugin = PluginMPL2()
    plugin.decompose(sub_path, movie_fps)
    subs = plugin.decomposed_subtitle
    plugin.decomposed_subtitle = None
    plugin.decomposed_subtitle = subs
    plugin.compose(movie_fps)
    print plugin.compose_subtitle[0]
    plugin.writeComposeSubs(ct_sub_path)
