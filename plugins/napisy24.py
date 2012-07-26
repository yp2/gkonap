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

# w wynikach otrzymanych z re powinnismy poszukac numeru cd/dvd - cd1, cd2 ...
# re będzię sparawdzane pokolejn dla każdego 
# od najbardziej ogólnego 
#

# (?P<title>.*) - łapie całość 
# (?P<title>.*)(?P<release>dvd.*|br.*|blu.*)
# 
# (?P<title>.*)(?:[\.|\[|\(|\{]{1}|\s{1})(?P<year>\d{4})(?:[\.|\]|\)|\}]{1}|\s{1})(?P<release>.*) - łapie z rokiem, release'em





class Napisy24(SubsDownloadBase):
    def __init__(self):
        super(Napisy24, self).__init__()
        
        self.name = 'Plugin napisy24.pl'
        self.description = 'Plugin for downloading susbs from napisy24.pl'
        self.plugin_subtype = 'napisy24'

    def run(self):
        pass
    
    
if __name__ == '__main__':
    import re
    import os
    
    file_name = []
    ext_video = ['.avi', '.3gp', '.asf', '.asx', '.divx', '.mkv', '.mov', '.mp4', '.mpeg', '.mpg', '.ogm', '.qt', '.rm', '.rmvb', '.wmv', '.xvid']
    movie_dir = '/media/ork_storage/filmy'
    re_ilosc_cd = re.compile(r'(?:cd|dvd|e|part|p)(?P<cd>(?:\d{1}|\s+?\d{1}))', re.IGNORECASE|re.UNICODE) 
    
    #od najbardziej szczegółowego 
    re_list = [
               '(?P<title>.*)(?:[\.|\[|\(|\{|\s]{1,2})(?P<year>\d{4})(?:[\.|\]|\)|\}|\s]{1,2})(?P<release>.*)',
               #'(?P<title>.*)(?:[\.|\[|\(|\{]{1}|\s{1})(?P<year>\d{4})(?:[\.|\]|\)|\}]{1}|\s{1})(?P<release>.*)',
               '(?P<title>.*?)[\.|\s]{1}(?P<release>(?:limited|proper|unrated|dvd|br|blu|cd).*)',
#               '(?P<title>.*)(?P<release>[\.|\s]{1}(?:proper.*|limited.*|unrated.*|dvd.*|br.*|blu.*))',
               '(?P<title>.*)',
               ]
    
    for r, d, f in os.walk(movie_dir):
        for n in f:
            if os.path.splitext(n)[1] in ext_video:
                name = os.path.split(n)[1]
                name = os.path.splitext(name)[0]
                file_name.append(name)
    
    re_list = [re.compile(r, re.IGNORECASE|re.UNICODE) for r in re_list]
    
    for m_name in file_name:
        for r in re_list:
            x = r.match(m_name)
            if x:
                dict = x.groupdict()
                d_title = dict.get('title')
                d_year = dict.get('year')
                d_release = dict.get('release')
                
                d_ele = [d_title, d_year, d_release]
                for ele in d_ele:
                    if ele:
                        cd_match = re_ilosc_cd.search(ele)
                        if cd_match:
                            cd_dict = cd_match.groupdict()
                            dict['cd'] = cd_dict.get('cd').strip()
                
                print 'Orygi\t: %s' % m_name
                print 'Title\t: %s' % dict.get('title')
                print 'Year\t: %s' % dict.get('year')
                print 'Release\t: %s' % dict.get('release')
                print 'CD\t: %s' % dict.get('cd')
                print '-'*80
                break
        
    
    
#    from urllib import urlopen, quote
#    from xml.dom.minidom import parse, parseString
#    import re
#    from xml.etree import cElementTree
##    p = Napisy24()
##    p.run()
#    
#    search1 = quote('true blood')
#    search2 = quote('true blood 01x01')
#    search3 = quote('The Iron Lady')
#    urlappi1 = 'http://napisy24.pl/libs/webapi.php?title=%s' % (search1)
#    urlappi2 = 'http://napisy24.pl/libs/webapi.php?title=%s' % (search2)
#    urlappi3 = 'http://napisy24.pl/libs/webapi.php?title=%s' % (search3)
#    
#    outappi1 = urlopen(urlappi1).read()
#    outappi2 = urlopen(urlappi2).read()
#    outappi3 = urlopen(urlappi3).readlines()
#    outappi1 = re.sub(r'<\?.*\?>', '', outappi1)
#    outappi1 = re.sub(r'\n|\t', '', outappi1) #usuwanasz białe znaki 
#    outappi1 = "<root>%s</root>" % outappi1
##    print outappi1
#    
#    xinput =  parseString(outappi1)
##    print outappi2
#    
#    class SUBS(object):
#        def __init__(self):
#            pass
#    def handleRoot(xinput):
#        subs = []
##        n = xinput.getElementsByTagName('root')
#        for e in cElementTree.fromstring(xinput):
#            for i in e.getiterator('subtitle'):
#                f = {}
#                for s in i.getchildren():
#                    f[s.tag] = s.text
#                
#                subs.append(f)
#        for sub in subs:
#            print sub['id'] +"\t" + sub['title'] +"\t" + sub['release']
#        
#        print subs
#        
#                
#        
#    def getText(nodelist):
#        rc = ""
#        for node in nodelist:
#            
#            if node.nodeType == node.TEXT_NODE:
#                rc = rc + node.data
#        return rc
#    
#    def handleSubTitle(title):
#        print 'tytuł - %s' % getText(title.childNodes)
#    
#    def handleSub(sub):
#        handleSubTitle(sub.getElementsByTagName('title')[0])    
#    
#    def handleSubs(subs):
#        for sub in subs:
#            handleSub(sub)
#    
#    handleRoot(outappi1)
    
#    print parseString(outappi2)
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
    