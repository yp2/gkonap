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

# Moduł odpowiedzialny za ściąganie napisów powstał na podstawie skryptu napisanego przez: 
#  - gim, 
#  - krzynio, 
#  - dosiu, 
#  - hash.
# Oryginalny skrypt można pobrać ze strony:
#
# http://hacking.apcoh.com/2008/01/napi_06.html
#
# Gratsy dla nich!!! 

import hashlib
import urllib
import os
from subprocess import Popen, PIPE

class Napiprojekt(object):
    def __init__(self):
        self.file_path = None
        self.subs_http = None
        self.arch_path = '/var/tmp/napisy.7z'
        
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
        @file_path - ścieżka do pliku wideo do którego 
                     będą ściagane napisy
        """
        
        movie_file = open(self.file_path).read(10485760)
        h = hashlib.md5()
        h.update(movie_file)
        
        link = "http://napiprojekt.pl/unit_napisy/dl.php?l=PL&f="+h.hexdigest()+"&t="+self.f(h.hexdigest())+"&v=other&kolejka=false&nick=&pass=&napios="+os.name
        self.subs_http = urllib.urlopen(link).read()
    
    def write_subs(self):
        open(self.arch_path, 'w').write(self.subs_http) #utowrzenie pliku z archiwum
        sub_path = os.path.splitext(self.file_path)[0] + ".txt" # utowrzenie nazwy dla pliku z napisami
        # podstawa nazwy taka sama rozszeżenie inne
        
        # utworzenie komendy dla 7z
        cmd = ['/usr/bin/7z x -y -so -piBlm8NTigvru0Jr0 %s 2>/dev/null >\"%s\"' % (self.arch_path, sub_path)]
        unpack = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        if unpack.wait():
            # nie udało ściągnąć się napisów do filmu
            # kasujemy powstały plik sub_path
            print "Brak napisów"
            os.remove(sub_path)
        else:
            # obrano napisy
            print "Napisy pobrano"
            
        os.remove(self.arch_path) # kasujemy pobrany plik 7z
    
    def run(self, file_path):
        self.file_path = file_path
        
        self.get_subs()
        self.write_subs()
        
        

if __name__ == '__main__':
    mkv = '/media/ork_storage/completed/True.Blood.S05E01.REPACK.720p.HDTV.x264-IMMERSE.mkv'
    napi = Napiprojekt()
    napi.run(mkv)
    