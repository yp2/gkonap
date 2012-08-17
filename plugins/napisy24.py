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

import re
import os
from urllib2 import urlopen, quote, HTTPError, URLError
from urllib import urlencode
import time
from xml.etree import cElementTree

from gkcore.subsdwn import SubsDownloadBase
from gkcore.info import get_fps

# w wynikach otrzymanych z re powinnismy poszukac numeru cd/dvd - cd1, cd2 ...
# re będzię sparawdzane pokolejn dla każdego 
# od najbardziej ogólnego 
#

# (?P<title>.*) - łapie całość 
# (?P<title>.*?)[\.|\s]{1}(?P<release>(?:limited|proper|unrated|dvd|br|blu|cd|repack).*)
# 
# (?P<title>.*?)(?:[\.|\[|\(|\{]{1}|\s{1})(?P<year>\d{4})(?:[\.|\]|\)|\}]{1}|\s{1})(?P<release>.*) - łapie z rokiem, release'em

# serial
#
# (?P<title>.*)
# (?P<title>.*?)S(?P<season>[0-9]{1,2})(?:\s|.)*?E(?P<episode>[0-9]{1,2})
#
# (?P<title>.*?)(?P<season>[0-9]{1,2})x(?P<episode>[0-9]{1,2})(?P<e_title>.*?)(?P<release>(?:720|1080|hdtv|blu|dvd|limited|proper|repack).*)
# (?P<title>.*?)S(?P<season>[0-9]{1,2})E(?P<episode>[0-9]{1,2})(?P<e_title>.*?)(?P<release>(?:720|1080|hdtv|blu|dvd|limited|proper|repack|ws|pdtv|x264|h264).*)




class Napisy24(SubsDownloadBase):
    def __init__(self):
        super(Napisy24, self).__init__()
        
        self.name = 'Plugin napisy24.pl'
        self.description = 'Plugin for downloading susbs from napisy24.pl'
        self.plugin_subtype = 'napisy24'
        self.multichoice = True
        self.choice = None
        self.subs = None
        
        self.release = '720|1080|hdtv|blu|brrip|dvd|cd|limited|proper|repack|part|(?:\.ws|\sws)|pdtv|x264|h264|unrated' # niezbędne do utorzenia wyrażenia regularnego
        # m_name - media_name
        self.str_re_m_name = [
            '(?P<title>.*)(?:.|\s){0,3}S(?P<season>[0-9]{1,2})(?:.|\s){0,3}E(?P<episode>[0-9]{1,2})(?P<eptitle>.*?)(?P<release>(?:%s).*)' % self.release,
            '(?P<title>.*)(?:.|\s){0,3}season(?P<season>[0-9]{1,2})(?:.|\s){0,3}episode(?P<episode>[0-9]{1,2})(?P<eptitle>.*?)(?P<release>(?:%s).*)' % self.release,
            '(?P<title>.*)(?:.|\s){0,3}(?P<season>[0-9]{1,2})(?:.|\s){0,3}x(?:.|\s){0,3}(?P<episode>[0-9]{1,2})(?P<eptitle>.*?)(?P<release>(?:%s).*)' % self.release,
            '(?P<title>.*)[.|\.|\[|\(|\{|\s]{1,2}(?P<year>\d{4})[.|\.|\]|\)|\}|\s]{1}(?P<release>.*)',
            '(?P<title>.*?)(?:\.|\s){0,2}(?P<release>(?:%s).*)' % self.release, # (?P<title>.*?) na końcu ważne '?' ściąga jak naj mniej
            '(?P<title>.*)(?:.|\s){0,3}S(?P<season>[0-9]{1,2})(?:.|\s){0,3}E(?P<episode>[0-9]{1,2})',
            '(?P<title>.*)(?:.|\s){0,3}S(?P<season>[0-9]{1,2})(?:.|\s){0,3}xE(?P<episode>[0-9]{1,2})',
            '(?P<title>.*)(?:.|\s){0,3}season(?P<season>[0-9]{1,2})(?:.|\s){0,3}episode(?P<episode>[0-9]{1,2})',
            '(?P<title>.*)'
                       ]
        self.re_m_parts = re.compile(r'(?:cd|dvd|part)(?P<cd>(?:\d{1}|\s+?\d{1}))', re.IGNORECASE|re.UNICODE)
        self.re_m_name = [re.compile(r, re.IGNORECASE|re.UNICODE) for r in self.str_re_m_name] # utworzone na podstawie str_re_m_name
        self.media_name = None # słownik z danymi o podanym pliku odczytanymi przez plugin (title, year, release itp)
        self.subs_language = 'pl'
        
    def get_subs(self):
        
        # określenie nazwy pliku video na podstawies ścieżki
        name_m = os.path.splitext(os.path.split(self.file_path)[1])[0]
        
        # przejście nazwy pliku video przez utowrzone wyrażenia regularne 
        # przejście następuje od najbardziej szczegółowego
        
        m_dict = None # zmiena do przetrzymywania danych słownika z dopasowania dla pliku video
        
        for re_exp in self.re_m_name:
            re_match = re_exp.match(name_m)
            if re_match: # znaleziono wzór
                m_dict = re_match.groupdict() # utowrzenie słownika zawierającego grupy z dopasowania (match)
                
                # dodanie fps do słownika
                m_dict['fps'] = str(get_fps(self.file_path))
                
                # dodanie rzomiaru do słownika
                m_dict['size'] = str(os.stat(self.file_path).st_size)
                
                # poszukiwanie danych release, year, title jeżeli nie ma ich w nazwie
                # pliku, będziemy szukać jej w nazwie katalogu o poziom niżej
                if not m_dict.get('release') or m_dict.get('year') or m_dict.get('title'):
                    # nie mamy danych o release, może jest w nazwie katalogu
                    dir_name = os.path.split(os.path.split(self.file_path)[0])[1]
                    for _re_exp in self.re_m_name:
                        dir_re_match = _re_exp.match(dir_name)
                        if dir_re_match:
                            d_m_dict = dir_re_match.groupdict()
                            if d_m_dict.get('release') and not m_dict.get('release'):
                                m_dict['release'] = d_m_dict.get('release')
                            if d_m_dict.get('year') and not m_dict.get('year'):
                                m_dict['relese'] = d_m_dict.get('year')
                            if d_m_dict.get('title') and not m_dict.get('title'):
                                m_dict['title'] = d_m_dict.get('title')
                            break
                
                # przeszukanie w poszukiwaniu numeru części jeżeli video składa
                # się z kilku odrebnych plików (z kilku płyt)
                    
                part_ele = [m_dict.get('title'), m_dict.get('release')]
                for ele in part_ele:
                    if ele: # jeżeli ele zawiera wartość 
                        part = self.re_m_parts.search(ele)
                        if part:
                            m_dict['cd'] = part.groupdict().get('cd') # utworzenie nowego klucza cd - okreslające część
                            
                break # znalezione dopasowanie wyskakujemy z pętli             
        
        if m_dict:
            # ustawienie media_name na podstawie danych ze słownika m_dict
            # uzyskanych z nazwy pliku przez plugin 
            self.media_name = m_dict
            self.clear_media_name()
            query = self.get_query() # utoworzenie listy z zapytaniami
            
            # zapytanie do serwera
            _subs = self.query_server(query) # wynik query_server w zmiennej _subs w celu
            # sprawdzenia czy zawiera jakieś dane jeżeli tak to nastąpi przypisanie do self.subs
            
            # przypisanie do zmiennej _subs do atrybutu self.subs 
            if len(_subs) != 0:
                self.subs = _subs
            else:
                print 'Brak napisów w napisy24.pl dla tego filmu'
            
        else:
            print "Nie udało się uzyskać inforamcji o pliku"
            
            
    def query_server(self, query):
        """
        
        @ query - lista z str zawiarające już zakodowane koncówki zapytań
        
        """
        self.subs = None # dla pewności reset zmiennej subs (do przetrzymywania wyików tej metody)
        
        _subs = {} # tymczasowa zmienna do przetrzymywania danych uzyskanych
        # podczas przetwarzania zapytań oraz odpowiedzi, jeżeli będą jakieś wyniki 
        # to zostanie ona przypisana do atrybut self.subs
        
        q_http = 'http://napisy24.pl/libs/webapi.php?%s' # na końcu wstawiamy dokładne zapytanie
        
        t = 1 # ilość powtórzeń. 
        
        # dla utorzonych zapytań od najbardziej szczegułowego 
        # wysyłamy zapytanie do serwera
        for q in query:
            # utworzenie url składającego się z bazy (wyżej) oraz uzyskanych zapytań w
            # form zakodowane dla http z metody get_query
            url = q_http % q
            
            try:
                h_subs = urlopen(url) # otwarcie danego url
                h_subs = h_subs.readlines() # wczytanie zawarości odpowiedzi
                
                # sprawdzamy czy mamy dobry wynik w odpowiedzi
                # jeżeli odpowiedź nie zawira żadnych wyników to pierwsza linie
                # brzmi "brak wynikow"
                if h_subs[0] != 'brak wynikow':
                    
                    #przekazanie odpowiedzi do obróbki i ustawienia 
                    s = self.handle_XML_response(h_subs)
                    _subs[t] = s
                    t += 1
                
            except (HTTPError, URLError), e:
                #błąd podaczas pobierania informacji o napisach 
                print e.reason
                self.subs = None # w przypadku błędu w pobieraniu ustawiamy None dla pobranych inforamcji o napisach
            
            time.sleep(0.5)
        
        return _subs # przypisanie do zmiennej self.subs nastąpi w met. self.get_subs
            
    def handle_XML_response(self, response):
        """
        Metoda przetwarza otrzymaną odpowiedż w poprawny XML, 
        następnie przetwarza dla postaci niezbędnej dla typu 
        przechowywanego w zmiennej self.subs, która ma służyć jako
        podstawa decyzju użytkownika/programu co do decyzji jakie
        napisy ściągnąć dla danego pliku wideo
        @ response - lista zawierająca poszczególne linie odpowiedzi od
        serwera
        """
        
        if response[0].startswith('\n'):
            response = response[1:] #usunięcie piwerwszej niepotrzebnej lini
        
        response.insert(1, '<root>') # w pozycji 1 dodanie elementu głównego dok. xml
        response.append('</root>') # tak mamy poprawny dok. XML
        response = ''.join(response) # łączymy poszczególne linie
        response = response.decode('CP1252').encode('UTF-8') # zakodowanie wyniku do UTF-8
        response = re.sub(r'\n|\t', '', response)
        
        for element in cElementTree.fromstring(response):
            for subelement in element.getiterator('subtitle'):
                subele_dict = {}
                for children in subelement.getchildren():
                    subele_dict[children.tag] = children.text
        
        return subele_dict
            
    def get_query(self):
        """
        Metoda zwaraca zapytania od jak najbardziej szczegółowych do
        najmniej szczegółowych.
        wynik ma postać listy łacuchów znaków przekszłaconych na 
        postać zgodną z linkami http przez metodę urllib.urlencode 
        """
        def get_none(obj):
            if obj == None or obj == 'None':
                return ''
            else:
                return obj
            
        season = self.media_name.get('season')
        episode = self.media_name.get('episode')
        url_query = [] # lista do przechowywania utworzonych częsci zapytań za pomocą urlencode
        if not season or not episode:
            # movie
            
            # listy uporządkowane są od najbardziej szczególowego zapytania
            query =[
                    ['title', 'release', 'size', 'cd'],
                    ['title', 'release', 'cd'],
                    ['title', 'release', 'size'],
                    ['title', 'size', 'cd'],
                    ['title', 'release'],
                    ['title', 'size'],
                    ['title', 'cd'],
                    ['title'],
                    ]
            for q_list in query:
                _q_dict = {} # słownik zostanie przekszłacony na zapytanie przez urlencode
                _q_dict['language'] = self.subs_language # język dla napisów
                for ele in q_list:
                    _q_dict[ele] = get_none(self.media_name.get(ele)) # mapowaniw poszczególnych danych na nowy słownik
                
                url_query.append(urlencode(_q_dict)) # utowrzenie oraz dodanie str po urlencode
            
        else:
            # tvshow
            query =[
                    ['title', 'release', 'size'],
                    ['title', 'release'],
                    ['title', 'size'],
                    ['title'],
                    ]
                    
            for q_list in query:
                _q_dict = {} # słownik zostanie przekszłacony na zapytanie przez urlencode
                _q_dict['language'] = self.subs_language # język dla napisów
                for ele in q_list:
                    if ele == 'title':
                        # dla tytułu musimy utowrzyć nowy tytuł zawierajacy 
                        # seson oraz odcinek w postaci seasonxepisode
                        value_ele = self.media_name.get(ele)
                        value_ele = '%s %sx%s' % (value_ele, season, episode)
                        _q_dict[ele] = get_none(value_ele)
                    else:
                        _q_dict[ele] = get_none(self.media_name.get(ele)) # mapowaniw poszczególnych danych na nowy słownik
                
                url_query.append(urlencode(_q_dict)) # utowrzenie oraz dodanie str po urlencode
        
        return url_query
                        
    def clear_media_name(self):
        """
        Metoda do czyszczenia słownika zawierającego 
        dane uzyskane przez plugin o podanym pliku 
        video. 
        Dane te potrzebnę są do utowrzenia zapytań
        """
        _re_clear = re.compile(r'\.', re.IGNORECASE|re.UNICODE)
        _re_clear_parts = re.compile(r'(?:cd|dvd|part)\d{1}', re.IGNORECASE|re.UNICODE)
        _re_clear_rel = re.compile('_', re.IGNORECASE|re.UNICODE)
        
        
        if self.media_name.get('title'):
            title = self.media_name['title']
            title = re.sub(_re_clear, ' ', title)
            title = re.sub(_re_clear_parts, '', title)
            title = title.strip('. ')
            self.media_name['title'] = title
        
        if self.media_name.get('eptitle'):
            eptitle = self.media_name['eptitle']
            eptitle = re.sub(_re_clear, ' ', eptitle)
            eptitle = eptitle.strip('. ')
            self.media_name['eptitle'] = eptitle
        
        if self.media_name.get('release'):
            release = self.media_name['release']
            release = re.sub(_re_clear_rel, '\.', release) 
            release = re.sub(_re_clear_parts, '', release)
            release = release.strip('. ')
            self.media_name['release'] = release
        
        _keys = ['year', 'season', 'episode', 'cd', 'fps']
        
        for k in _keys:
            if self.media_name.get(k):
                ele = self.media_name[k]
                ele = ele.strip('. ')
                self.media_name[k] = ele
    
    def reset(self):
        super(Napisy24, self).reset()
        self.media_name= None
    
if __name__ == '__main__':
    
    
    file_name = []
    ext_video = ['.avi', '.3gp', '.asf', '.asx', '.divx', '.mkv', '.mov', '.mp4', '.mpeg', '.mpg', '.ogm', '.qt', '.rm', '.rmvb', '.wmv', '.xvid']
    movie_dir = '/media/ork_storage/filmy'
    tv_dir = '/media/ork_storage/tv'
    movie_dir = tv_dir
    pn24 = Napisy24()
    for r,d,f in os.walk(movie_dir):
        for n in f:
            f_path = os.path.join(r,n)
            if os.path.splitext(f_path)[1] in ext_video:
                pn24.file_path = f_path
                pn24.get_subs()
                print pn24.file_path
                if pn24.subs:
                    for k,v in pn24.subs.iteritems():
                        print k
                        for xk, xv in v.iteritems():
                            print '%s\t\t:%s' % (xk, xv)
                    print '-'*80
                else:
                    print "brak napisów"
                pn24.reset()
                
                


#release = '720|1080|hdtv|blu|brrip|dvd|cd|limited|proper|repack|ws|pdtv|x264|h264|unrated'
    #re_ilosc_cd = re.compile(r'(?:cd|dvd|part)(?P<cd>(?:\d{1}|\s+?\d{1}))', re.IGNORECASE|re.UNICODE) 
    #
    #od najbardziej szczegółowego 
    #re_list = [
#               '(?P<title>.*)(?:.|\s){0,3}S(?P<season>[0-9]{1,2})(?:.|\s){0,3}E(?P<episode>[0-9]{1,2})(?P<e_title>.*?)(?P<release>(?:%s).*)' % release,
#               '(?P<title>.*)(?:.|\s){0,3}(?P<season>[0-9]{1,2})(?:.|\s){0,3}x(?:.|\s){0,3}(?P<episode>[0-9]{1,2})(?P<e_title>.*?)(?P<release>(?:%s).*)' % release,
#
#               '(?P<title>.*)[.|\.|\[|\(|\{|\s]{1,2}(?P<year>\d{4})[.|\.|\]|\)|\}|\s]{1}(?P<release>.*)',
#               '(?P<title>.*?)(?:\.|\s){0,2}(?P<release>(?:%s).*)' % release, # (?P<title>.*?) na końcu ważne '?' ściąga jak naj mniej
#               
#               '(?P<title>.*)(?:.|\s){0,3}S(?P<season>[0-9]{1,2})(?:.|\s){0,3}E(?P<episode>[0-9]{1,2})',
#               
#               '(?P<title>.*)',
#               ]
    
    #zamiana katologów na potrzeby seriali
#    movie_dir = tv_dir
    
    
#    for r, d, f in os.walk(movie_dir):
#        for n in f:
#            if os.path.splitext(n)[1] in ext_video:
#                print r, d, n
#                name = os.path.split(n)[1]
#                name = os.path.splitext(name)[0]
#                file_name.append(name)
    
#    re_list = [re.compile(r, re.IGNORECASE|re.UNICODE) for r in re_list]
    
#    for n in file_name:
#        print n
    
#    for m_name in file_name:
#        for r in re_list:
#            x = r.match(m_name)
#            if x:
#                dict = x.groupdict()
#                d_title = dict.get('title')
#                d_year = dict.get('year')
#                d_release = dict.get('release')
#                d_season = dict.get('season')
#                d_episode = dict.get('episode')
#                d_e_title = dict.get('e_title')
#                
#                d_ele = [d_title, d_year, d_release]
#                for ele in d_ele:
#                    if ele:
#                        cd_match = re_ilosc_cd.search(ele)
#                        if cd_match:
#                            cd_dict = cd_match.groupdict()
#                            dict['cd'] = cd_dict.get('cd').strip()
#                
#                print 'Orygi\t: %s' % m_name
#                print 'Title\t: %s' % dict.get('title')
#                print 'Year\t: %s' % dict.get('year')
#                print 'Release\t: %s' % dict.get('release')
#                print 'Season\t: %s' % dict.get('season')
#                print 'Episode\t: %s' % dict.get('episode')
#                print 'E title\t: %s' % dict.get('e_title')
#                print 'CD\t: %s' % dict.get('cd')
#                print '-'*80
#                break
#        
    
#    
#    from urllib import urlopen, quote
#    from xml.dom.minidom import parse, parseString
#    import re
#    from xml.etree import cElementTree
##    p = Napisy24()
##    p.run()
#    
#    search1 = quote('Star.wars')
#    search2 = quote('true blood 01x01')
#    search3 = quote('The Iron Lady')
#    urlappi1 = 'http://napisy24.pl/libs/webapi.php?title=%s' % (search1)
#    urlappi2 = 'http://napisy24.pl/libs/webapi.php?title=%s' % (search2)
#    urlappi3 = 'http://napisy24.pl/libs/webapi.php?title=%s' % (search3)
#    
#    outappi1 = urlopen(urlappi1).readlines()
#    outappi2 = urlopen(urlappi2).read()
#    outappi3 = urlopen(urlappi3).readlines()
##    outappi1 = re.sub(r'<\?.*\?>', '', outappi1)
##    outappi1 = re.sub(r'\n|\t', '', outappi1) #usuwanasz białe znaki 
##    outappi1 = "<root>%s</root>" % outappi1
#    if outappi1[0].startswith('\n'):
#        outappi1 = outappi1[1:]
#        outappi1.insert(1, '<root>')
#        outappi1.append('</root>')
#        outappi1 = ''.join(outappi1)
#        outappi1 = outappi1.decode('CP1252').encode('UTF-8')
#        outappi1 = re.sub(r'\n|\t', '', outappi1)
#    print outappi1
#    
##    xinput =  parseString(outappi1)
##    print outappi2
#    
#    class SUBS(object):
#        def __init__(self):
#            pass
#        
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
    