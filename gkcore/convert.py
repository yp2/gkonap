#!/usr/bin/env python
#-*- coding: utf-8 -*-

#       gkcore.convert
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

class ConvertBase:
    """
    Base class for plugins to convert subtitles. 
    """
    def __init__(self):
        """
        
        """
        pass
    
    def __unicode__(self):
        """
        Return plugin type - subtitle type 
        """
        #rozwiązać jak ma się nazywać to co zwraca ta metoda i jak to napisać
        #czy self czy tylko w tej metodzie zwraca nazwę pluginu
        pass
        
    
    def recognize(self, subtitle_file):
        """
        Methode for recognizing the type of subtitles.
        subtitle_file - subtitle file opened for read
        """
        pass
    
    def decode(self, movie_fps, subtitle_file):
        """
        Methode for decoding the subtitles.
        Returns: start_time, stop_time, subtitle content
        movie_fps - fps of video file or given fps for subtitle file
        """
        pass
    
    def subProcesing(self):
        """
        Methode for processing subtitles content eg. removing 
        some unnecesary decorators from subtitles, replace some
        parts of subtitles ...
        """
        # implementujemy tu całość
        pass
    def code(self, movie_fps):
    
        