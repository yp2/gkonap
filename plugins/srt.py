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
try:
    from cdecimal import Decimal, ROUND_DOWN
except ImportError:
    from decimal import Decimal, ROUND_DOWN


class PluginSRT(ConvertBase):
    def __init__(self):
        super(PluginSRT, self).__init__()
        
        self.name = "Plugin SRT"
        self.description = "Plugin for SubRip Format of subtitles"
        self.subtype = 'srt'
        self.re_subs_type = r'^\d{1}$'
        self.re_decompose_subs = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n')
        self.compose_line = '%i\n%s --> %s\n%s\n\n'
        
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
        
        #post processing
        self.postDecomposeProcsessing()
        
#        print self.decomposed_subtitle[1]
        
    def decomposeTimeConversion(self, time, movie_fps=None):
        '''
        Zwraca sekundy w Decimal
        '''
        _re_time = re.compile('(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2}),(?P<msec>\d{3})')
        _re_time = _re_time.match(time)
        _re_time = _re_time.groupdict()
        _t_hour = float(_re_time['hour'])
        _t_min = float(_re_time['min'])
        _t_sec = float(_re_time['sec'])
        _t_msec = int(_re_time['msec']) * 0.001
        conv_time = (_t_hour * 3600) + (_t_min * 60) + _t_sec + _t_msec
        conv_time = Decimal(str(conv_time))
        
        return conv_time.quantize(Decimal('1.000'), rounding=ROUND_DOWN)
    
    def preDecomposeProcessing(self):
        #delete first line in srt type of subs 
        #subs converted to list
        self.subtile_file = list(self.subtile_file)[1:]
        
        super(PluginSRT, self).preDecomposeProcessing()
        
        # subs type specific pre processing
        # remove marks of linies
        self.joined_sub = re.sub(r'\n{2}\d*\n', '', self.joined_sub)
        
    def compose(self, movie_fps):
        super(PluginSRT, self).compose(movie_fps)
        
        #decopmse to lista w liście - [[], [], ...]
        #wewnętrzne listy oznaczają poszczególne linie
        
        #w tym miejscu jest ostatnia możliwość zmiany czegoś w lini napisów
        #chodzi o metoda subProcessing
        self.subProcesing()
        
        _compose_subs = []
        _sub_count = 1
        while self.decomposed_subtitle:
            sub_line = self.decomposed_subtitle[0]
            time_start = self.composeTimeConversion(sub_line[0], movie_fps)
            time_stop = self.composeTimeConversion(sub_line[1], movie_fps)
            line = self.composeLineConversion(sub_line[2])
            
            # '%i\n%s --> %s\n%s\n\n'            
            conv_line = self.compose_line % (_sub_count, time_start, time_stop, line)
            _compose_subs.append(conv_line)
           
            _sub_count += 1
            self.decomposed_subtitle = self.decomposed_subtitle[1:]
            
        self.compose_subtitle = _compose_subs
            
    def composeTimeConversion(self, time, movie_fps):
        """
        Metdoa do konwersji czasu dla danego formatu 
        wynik w postaci gotowy do wstawienia do szablonu napisu
        @time = czas w sekundach uwaga w formacie Decimal
        @movie_fps = ilość klatek na sekundę
        """
        
#        time = str(time)
#        second = int(re.split("\.", time, )[0])
#        msecond = re.split("\.", time)[1]
#        
#        if len(msecond) == 1:
#            msecond = msecond + '00'
#        if len(msecond) == 2:
#            msecond = msecond + '0'
#        
#        minute = int(second/60)
#        hour = int(minute/60)
#        
#        second = second - (minute*60)
#        minute = minute - (hour*60)
#        msecond = int(msecond)
#        

        msecond = time * 1000
        
        hour = msecond // (3600000)
        msecond %= (3600000)
        minute = msecond // (60000)
        msecond %= (60000)
        second = msecond / (1000)
        msecond %= (1000)
        
        conv_time = "%02d:%02d:%02d,%03d" % (hour, minute, second, msecond)
        return conv_time
    
    def composeLineConversion(self, line):
        """
        Methoda do zamieniania elementów w lini napisów
        | na \n 
        """
        out = re.sub(r'\|', '\n', line)
        return out
        
        
if __name__ == '__main__':
    import cProfile
    import pstats
    
    sub_path = '/home/daniel/git/gkonap/test_files/srt.srt'
    ct_sub_path = '/home/daniel/git/gkonap/test_files/ct_srt.srt'
    movie_fps = 23.976
    plugin = PluginSRT()
    
    
    
    plugin.decompose(sub_path, movie_fps)
    print plugin.decomposed_subtitle[1275]
    subs = plugin.decomposed_subtitle
    
#    plugin.decomposed_subtitle = None
#    plugin.decomposed_subtitle = subs
#    plugin.compose(movie_fps)
    
#    
#    plugin.writeComposeSubs(ct_sub_path)
    
    
    cProfile.run('plugin.decompose(sub_path, movie_fps)', 'stat_decompose')
   
    d = pstats.Stats('stat_decompose')
    d.sort_stats('name')
    d.strip_dirs()
    d.print_stats('decomposeTimeConversion')
#
    cProfile.run('plugin.compose(movie_fps)', 'stat_compose')    
    c = pstats.Stats('stat_compose')
    c.sort_stats('name')
    c.strip_dirs()
    c.print_stats('composeTimeConversion')
    
    print plugin.compose_subtitle[1275]
    
    

    
    
    
