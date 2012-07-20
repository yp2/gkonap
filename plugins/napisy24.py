#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
#       plugins.napisy24
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

from gkcore.subsdwn import SubsDownloadBase
import urllib
import HTMLParser
from xml.dom.minidom import parse, parseString


class Napisy24(SubsDownloadBase):
    def __init__(self):
        super(Napisy24, self).__init__()
        
        self.name = 'Plugin napisy24.pl'
        self.description = 'Plugin for downloading susbs from napisy24.pl'
        self.subtype = 'napisy24'

    def run(self):
        pass
    
    
if __name__ == '__main__':
#    p = Napisy24()
#    p.run()
    
    search1 = 'true blood'
    search2 = 'true blood 01x01'
    search3 = 'The Iron Lady'
    url1 = 'http://napisy24.pl/search.php?str=%s' % (search1)
    url2 = 'http://napisy24.pl/search.php?str=%s' % (search2)
    urlappi1 = 'http://napisy24.pl/libs/webapi.php?title=%s' % (search1)
    urlappi2 = 'http://napisy24.pl/libs/webapi.php?title=%s' % (search2)
    urlappi3 = 'http://napisy24.pl/libs/webapi.php?title=%s' % (search3)
    
#    out1 = urllib.urlopen(url1).readlines()
#    out2 = urllib.urlopen(url2).readlines()
    outappi1 = urllib.urlopen(urlappi1).readlines()
    outappi2 = urllib.urlopen(urlappi2).readlines()
    outappi3 = urllib.urlopen(urlappi3).readlines()
#    out1 = ''.join(out1)
#    out2 = ''.join(out2)
    outappi1 = ''.join(outappi1)
    outappi2 = ''.join(outappi2)
    outappi3 = ''.join(outappi3)
    print outappi1
    print outappi2
    print outappi3
#    print out1
#    print out2
#    class ParserN24(HTMLParser.HTMLParser):
#        def handle_starttag(self, tag, attrs):
#            if tag == 'a':
#                print "start tag        :", tag
#                for a in attrs:
#                    print '        atr    :', a
##            print "start tag        :", tag
##            for a in attrs:
##                print '        atr    :', a
#        def handle_data(self, data):
#            print 'data             :', data
##            
#    par = ParserN24()
#    par.feed(out1)
    