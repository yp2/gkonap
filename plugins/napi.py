#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
#       plugins.napi
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

# Plugin powstał na podstawie skryptu napisanego przez: 
# 2009 Arkadiusz Miskiewicz <arekm@pld-linux.org>
# Oryginał został mocno poprawiony
# Wielkie dzięki
# Plugin już nie potrzebuje 7z napisy ściągane są w postacji nie spakowanej

import hashlib
import urllib
import os
import time
from gkcore.subsdwn import SubsDownloadBase


class Napiprojekt(SubsDownloadBase):
    def __init__(self):
        super(Napiprojekt, self).__init__()
        
        self.name = 'Plugin napiprojekt.pl'
        self.description = 'Plugin for downloading subs from napiprojket.pl'
        self.plugin_subtype = 'napiprojket'
        self.multichoice = False
        self.subs = None
        self.subs_http = None
        
    def f(self, z):
        idx = [ 0xe, 0x3,  0x6, 0x8, 0x2 ]
        mul = [   2,   2,    5,   4,   3 ]
        add = [   0, 0xd, 0x10, 0xb, 0x5 ]
    
        b = []
        for i in xrange(len(idx)):
            a = add[i]
            m = mul[i]
            i = idx[i]
    
            t = a + int(z[i], 16)
            v = int(z[t:t+2], 16)
            b.append( ("%x" % (v*m))[-1] )
    
        return ''.join(b)
    
    def get_subs(self):
        """
        """
        # TODO: Dodać wyjątek do sprawdzania czy self.file_path jest róźny od None
        # aby plugin nie wyrzucał błędu
        movie_file = open(self.file_path).read(10485760)
        h = hashlib.md5()
        h.update(movie_file)
        
        link = "http://napiprojekt.pl/unit_napisy/dl.php?l=PL&f=%s&t=%s&v=pynapi&kolejka=false&nick=&pass=&napios=%s" % \
        (h.hexdigest(), self.f(h.hexdigest()), os.name)

        repeat = 3
        self.subs_http = None # dla pewnośći zerujemy zmienną
        
        while repeat > 0 :
            try:
                self.subs_http = urllib.urlopen(link)
                if hasattr(self.subs_http, "getcode"):
                    http_code = self.subs_http.getcode()
    
                    if http_code != 200: # sprawdzamy kod odpowiedzi 
                        print "Pobranie napisów nie powidoło się, odpowiedź HTTP %s" % http_code
                        time.sleep(0.5)
                        repeat =- 1
                        self.subs_http = None # zerujemy zmienną dla kolejnego cyklu 
                        continue
                    
                    self.subs_http = self.subs_http.read() # wczytanie wyniku
                    #sprawdzanie czy wynik jest dobry
                    if self.subs_http.startswith('NPc'):
                        print "Nie znaleziono napisów" 
                        repeat = 0 # brak napisów nie ma co ponownie szukać
                        self.subs_http = None
                        continue
                    
                    if self.subs_http is None or self.subs_http == "":
                        print "Poberanie napisów nie powiodło się"
                        repeat =-1 
                        self.subs_http = None
                        continue
                    
                    # sprwdzanie wyszło ok 
                    print "Napisy pobrane pomyślnie"
                    
                    # Ustawnienie atrybutu self.subs okrślającego jakie
                    # napisy ściągnąć w przypadku gdy self.multichoce = True
                    # w przypadku multichoice False zawsze będzie to jedna opcja
                    
                    self.subs_path = os.path.splitext(self.file_path)[0] + '.txt' # ścieżka do pliku napisów
                    subs_name = os.path.split(self.subs_path)[1]
                    
                    self.subs = {1:{
                                    'title':subs_name,
                                    'plugin': self.plugin_subtype,
                                    }
                                 }
                    
                    break # napisy pobrane nie potrzebujemy dalszej pętli
            except (IOError, OSError):
                print  "Pobranie napisów nie powidoło się."
                repeat =- 1
                self.subs_http = None
                time.sleep(0.5)
                continue
            
    def download_subs(self):
        # plugin nie daje wyboru napisów, jężeli są to 
        # są już ściagniete 
        if not self.multichoice:
            pass
    
    def write_subs(self):
        if self.subs_http:
            subs_save = open(self.subs_path, 'w') # utworzenie pliku
            subs_save.write(self.subs_http)
            subs_save.close()
            
        # resetujemy kluczowe atrybuty pluginu
        self.reset()
    
    def reset(self):
        super(Napiprojekt, self).reset()
        self.subs_http = None
        
if __name__ == '__main__':
    mkv = '/media/ork_storage/completed/True.Blood.S05E01.REPACK.720p.HDTV.x264-IMMERSE.mkv'
    napi = Napiprojekt()
#    napi.run(mkv)
    napi.file_path = mkv
    napi.get_subs()
    print napi.subs_http
    print napi.subs[1]['title']
    