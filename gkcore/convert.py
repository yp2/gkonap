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

import re
import os

class ConvertBase(object):
    """
    Base class for plugins to convert subtitles. 
    """    
    def __init__(self):
        
        #implement name and plugin_subtype in plugin subclass
        self.type = "convert"
        self.name = None
        self.description = None
        self.plugin_subtype = None
        
        #holds subs after decomposing to universal format
        self.decomposed_subtitle = None
        
        #re for finding subs type
        self.re_subs_type = None
        
        #re for decompose of subs - re.compile
        self.re_decompose_subs = None
        
        #holds subs after composing to susb format (list of strings)
        self.compose_subtitle = None
        
        #holds schema for line construction
        self.compose_line = None
        
        # holds corect subtitle file extension
        self.subs_file_ext = None
        
    def clear(self):
        """
        Metoda do zerowanie pluginu
        Wstawi None w poszczególne atrybuty 
        """
        self.decomposed_subtitle = None
        self.compose_subtitle = None
        
    def pluginType(self):
        return self.type
    
    def pluginName(self):
        return self.name
    
    def pluginSubType(self):
        return self.plugin_subtype
    
    def recognize(self, subtitle_file_path):
        """
        Methode for recognizing the type of subtitles.
        @subtitle_file_path - path to subtitle file
        Return subs type definied in each plugin_subtypein atr plugin_subtype.
        If subs are not recognize returns None
        """
        _re_subs_type = re.compile(self.re_subs_type)
        
        # dodanie możliwości sprawdzania nie tylko pliku ale także 
        # file-like objects 
        if type(subtitle_file_path) == str and os.path.isfile(subtitle_file_path):
            subtitle_file = open(subtitle_file_path, 'rU')
        else:
            subtitle_file = subtitle_file_path
        
        sub_first_line = subtitle_file.readline()
        
        if type(subtitle_file_path) == str and os.path.isfile(subtitle_file_path):
            subtitle_file.close()
            
        if _re_subs_type.search(sub_first_line):
            return self.plugin_subtype
        else:
            return None
    
    def checkExt(self, subtitle_file_path):
        """
        Methode to check ext of files, if ext are diferent than daclared in 
        self.subs_file_ext
        """
        if os.path.isfile(subtitle_file_path):
            if os.path.splitext(subtitle_file_path)[1] != self.subs_file_ext:
                old = subtitle_file_path
                nwe = os.path.splitext(subtitle_file_path)[0] + self.subs_file_ext
                os.rename(old, new)
        
    def decompose(self, subtitle_file_path, movie_fps):
        """
        Methode for decoding the subtitles.
        Returns: start_time, stop_time, subtitle content
        movie_fps - fps of video file or given fps for subtitle file
        """
        # Open subtitle file
        self.subtile_file = open(subtitle_file_path, 'rU')
    
    def preDecomposeProcessing(self):
        """
        Method for pre decompose procesing of subtitles.
        """
        
        #Join substitle in one string for future processing
        self.joined_sub = ''.join(self.subtile_file)
        
    def postDecomposeProcsessing(self):
        """
        Methode for post decompose processing of subs
        """
        #dla ujednolicenia formatu ogólnego brak znaków nowej lini
        # na końcach napisów
        # w środku zasąpienie '\n' - '|' jak znak podziału napisu
        
        for line in self.decomposed_subtitle:
            line[2] = line[2].rstrip()
            #zamiana '\n' na '|"
            line[2] = re.sub(r'\n', '|', line[2])
    
    def subProcesing(self):
        """
        Methode for processing subtitles content eg. removing 
        some unnecesary decorators from subtitles, replace some
        parts of subtitles ...
        """
        # implementujemy tu całość
        pass
    
    def compose(self, movie_fps):
        """
        Methode for converting subtitles to right format
        Najpierw aby metoda zadziałała trzeba przypisać do 
        plugin.decompose_subs rozłożone napisy
        """
        if self.decomposed_subtitle == None:
            raise AttributeError, 'Brak przypisanych napisów do zmiennej decompose_subtitle'
    
    def writeComposeSubs(self, sub_out_path):
        if not self.compose_subtitle:
            raise AttributeError, 'Brak napisów do zapisania.'
        
        out_file = open(sub_out_path, 'w')
        out_file.writelines(self.compose_subtitle)
        out_file.close()