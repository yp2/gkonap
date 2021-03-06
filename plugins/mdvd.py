#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
#       plugins.mdvd
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


class PluginMDVD(ConvertBase):
    def __init__(self):
        super(PluginMDVD, self).__init__()

        self.name = "Plugin MDVD"
        self.description = "Plugin for MicroDvd format of subtitles"
        self.plugin_subtype = "mdvd"
        self.re_subs_type = r'^\{\d*\}'
        self.re_decompose_subs = re.compile(r'\{(\d*)\}\{(\d*)\}')
        self.compose_line = '%s%s%s\n'
        self.subs_file_ext = '.txt'

    def decompose(self, subtitle_file_path, movie_fps):
        super(PluginMDVD, self).decompose(subtitle_file_path, movie_fps)

        self.pre_decompose_processing()

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
            time_start = self.decompose_time_conversion(_decompose_subs[0],
                                                        movie_fps)
            time_stop = self.decompose_time_conversion(_decompose_subs[1],
                                                       movie_fps)
            sub_line = _decompose_subs[2]
            line = [time_start, time_stop, sub_line]
            _decompose_subs_lines.append(line)
            _decompose_subs = _decompose_subs[3:]

        self.decomposed_subtitle = _decompose_subs_lines

        #post processing
        self.post_decompose_procsessing()

    def decompose_time_conversion(self, frame_number, movie_fps):
        #format klatkowy czyli frame_number/movie_fps = time w sek
        movie_fps = Decimal(str(movie_fps))
        conv_time = Decimal(frame_number) / movie_fps
        return conv_time

    def pre_decompose_processing(self):
        super(PluginMDVD, self).pre_decompose_processing()

    def compose(self, movie_fps):
        super(PluginMDVD, self).compose(movie_fps)

        #decopmse to lista w liście - [[], [], ...]
        #wewnętrzne listy oznaczają poszczególne linie

        #w tym miejscu jest ostatnia możliwość zmiany czegoś w lini napisów
        #chodzi o metoda subProcessing
        self.sub_procesing()

        _compose_subs = []
        while self.decomposed_subtitle:
            sub_line = self.decomposed_subtitle[0]
            time_start = self.compose_time_conversion(sub_line[0], movie_fps)
            time_stop = self.compose_time_conversion(sub_line[1], movie_fps)
            line = sub_line[2]

            # '%s%s%s'
            conv_line = self.compose_line % (time_start, time_stop, line)
            _compose_subs.append(conv_line)

            self.decomposed_subtitle = self.decomposed_subtitle[1:]

        self.compose_subtitle = _compose_subs

    def compose_time_conversion(self, time, movie_fps):
        movie_fps = Decimal(str(movie_fps))
        conv_time = time * movie_fps
        conv_time = '{%d}' % conv_time.quantize(Decimal('1'))
        return conv_time


if __name__ == "__main__":
    sub_path = '/home/daniel/git/gkonap/test_files/mdvd.txt'
    ct_sub_path = '/home/daniel/git/gkonap/test_files/ct_mdvd.txt'
    movie_fps = 23.976
    plugin = PluginMDVD()
    plugin.decompose(sub_path, movie_fps)
    subs = plugin.decomposed_subtitle
    print subs[1]
    plugin.decomposed_subtitle = None
    plugin.decomposed_subtitle = subs
    plugin.compose(movie_fps)
    print plugin.compose_subtitle[1]
#    plugin.writeComposeSubs(ct_sub_path)
