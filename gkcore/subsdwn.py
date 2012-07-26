#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
#       gkcore.subsdwn
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

class SubsDownloadBase(object):
    """
    Base class for plugins to download subs
    
    Używanie:
    ...
    
    
    
    """
    def __init__(self):
        
        #implement in plugin
        self.type = 'subsdwn'
        self.name = None
        self.description = None
        self.plugin_subtype = None
        self.multichoice = False
        self.choice = None
        
        #plugin specyfic
        self.file_path = None # path to video file
    
    def get_subs(self):
        """
        Metoda do pobierania informacji o napisach 
        dla danego pliku video
        Najpierw musi być ustwiony atrybut file_path
        dla pluginu
        """
        raise NotImplementedError
    
    def download_subs(self):
        """
        Metoda do ściąganie wybranego pliku z napisami
        na podstawie opcji self.choice
        Najpier trzeba ustawić self.choice
        """
        raise NotImplementedError
    
    def write_subs(self):
        """
        Metoda do zapisanie wybranego pliku napisów
        na podstawie decyzji użytkownika/programu 
        Wybór zapisany w self.choice
        """