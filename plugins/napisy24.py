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
import zipfile

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
        self.choice = None # !!! ważne przekazywać tylko int
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
        self.subs_dwn_link = 'http://napisy.me/download/' # należy dodać jeszcze typ oraz id napisów
        self.subs_dwn_type = None # typ napisów do ściągnięcia !!! ważne przekazywać int
        self.subs_type = {1 : 'mdvd',
                          2 : 'tmp',
                          3 : 'mpl2',
                          4 : 'sr'} # 1 - microDVD, 2 - TMplayer, 3 - MPL2, 4 - SubRip 
    
        self.ext_video = ['.avi', '.3gp', '.asf', '.asx', '.divx', '.mkv', '.mov', '.mp4', '.mpeg', '.mpg', '.ogm', '.qt', '.rm', '.rmvb', '.wmv', '.xvid']
                                    
        
        
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
    
    def download_subs(self):
        """
        Metoda do ściągania wybranego napisu. Wybór na podstawie 
        atrybutu self.choice oraz typu napisów self.subs_dwn_type
        """
        # plugin ściąga podane napisy na podstawie
        # self.choice oraz  obecności danych w self.subs
        if self.choice and self.subs and self.subs_dwn_type:
            # utworzenie linka http
            # link http http://napisy.me/download/mdvd/61111/
            
            _subs = self.subs[self.choice]                  # wybór danych napisów
            _subs_id = _subs['id']                               # id danych napisów
            _subs_type = self.subs_type[self.subs_dwn_type] # jakie maja być ściągnięte
            
            _http_dwn = self.subs_dwn_link + "%s/%s/" % (_subs_type, _subs_id)
            _tmp_zip = '/tmp/n24.zip'
            
            if os.path.exists(_tmp_zip):
                # jeżeli istneje już taki plik najpierw go kasujemy
                os.remove(_tmp_zip)
                
            try:
                _dwn_subs = urlopen(_http_dwn)
                self.save_zip_file_http(_dwn_subs, _tmp_zip)
                print 'Napisy pomyślnie ściągnięte'
            except (HTTPError, URLError), e:
                print e.reason
                
            if os.path.exists(_tmp_zip):
                _subs_from_zip = []
                # istnieje zachowane archiwum
                # należy je otworzyć
                if zipfile.is_zipfile(_tmp_zip):
                    #sprawdzenie czy plik to archiwum zip
                    _zfile = zipfile.ZipFile(_tmp_zip, mode='r')

                    for _ele_zfile in _zfile.infolist():
                        if not re.search(r'napisy24.pl', _ele_zfile.filename, re.I):
                            #plik nie zawiera w nazwie czyli wlaściwy plik z napisami
                            _subs_from_zip.append(_ele_zfile)
                    
                    if _subs_from_zip:
                        # sprawdzamy czy _subs_from_zip na jakieś elementy
                        
                        _subs_in_zip_file = len(_subs_from_zip)
                        
                        if _subs_in_zip_file == 1:
                            # jeden plik z napisami rozpakuj
                            # otwieramy dany plik na podstawie obiektu ZipInfo jedyny element w _subs_from_zip
                            _subs_zip_file = _zfile.open(_subs_from_zip[0], 'rU').readlines()
                            
                            # utworzenie ścieżki oraz nazyw pliku
                            _subs_path = os.path.splitext(self.file_path)[0]
                            _subs_ext_from_zip = os.path.splitext(_subs_from_zip[0].filename)[1]
                            _subs_path = _subs_path + _subs_ext_from_zip
                            
                            # otwieramy plik do zapisu dla pliku z napisami o utowrzonej scieżce
                            _subs_file = open(_subs_path, 'w').writelines(_subs_zip_file)
                            
                            print "Napisy pomyślnie rozpakowane"
                            
                            #zamykamy archiwum
                            _zfile.close()
                        
                        elif _subs_in_zip_file > 1:
                            # posiadamy kilka plików z napisami media wielopłytowe
                            # w arch zip plik z napisami sa już posortowane
                            
                            # ścieżka do katalogu, nazwa pliku   
                            _dir, _file = os.path.split(self.file_path)
                            # listujemy katalog z plikami 
                            _dir_ls = os.listdir(_dir)
                            # usuwamy z listy wszystkie pliki nie bedące pikami video       
                            _dir_ls = [ele for ele in _dir_ls if os.path.splitext(ele)[1] in self.ext_video]
                            # sortujemy listę z nazwami plików wideo
                            _dir_ls = sorted(_dir_ls)
                            
                            while _subs_from_zip:
                                # otwieramy dany plik na podstawie obiektu ZipInfo jedyny element w _subs_from_zip
                                _subs_zip_file = _zfile.open(_subs_from_zip[0], 'rU').readlines()
                                
                                try:
                                    # utworzenie ścieżki oraz nazyw pliku
                                    _subs_path = os.path.join(_dir, os.path.splitext(_dir_ls[0])[0]) # pierwszy element z listowania katalogu
                                    _subs_ext_from_zip = os.path.splitext(_subs_from_zip[0].filename)[1]
                                    _subs_path = _subs_path + _subs_ext_from_zip
                                
                                    # otwieramy plik do zapisu dla pliku z napisami o utowrzonej scieżce
                                    _subs_file = open(_subs_path, 'w').writelines(_subs_zip_file)
                                except IndexError:
                                    # nie ma już więcej plików wideo
                                    # resztę zapisujemy pod org nazwami z pliku zip
                                    _subs_path = _dir + _subs_ext_from_zip[0].filename
                                    _subs_file = open(_subs_path, 'w').writelines(_subs_zip_file)
                                
                                _subs_from_zip = _subs_from_zip[1:]
                                _dir_ls = _dir_ls[1:]
                            
                            print "Napisy pomyślnie rozpakowane"
                        else:
                            print "Brak napisów w archiwum"
                    else:
                        print "Brak napisów w archiwum"
                else:
                    print "Niepoprawne archiwum zip z napisami"
            else:
                print "Brak archiwum z napisami"
        else:
            print "Brak danych potrzebnych do ściągniacia napisów"
    
    def save_zip_file_http(self, http_file_obj, save_path):
        """
        Funkcja do zapisywania otrzymanego objektu po wykonaniu zapytania.
        Ściąga i zapisuje plik zip do podanej ścieżki
        @ http_file_obj - obiekt file-like otrzymany po wykonaniu zapytania
        @ save_path - ścieżka do zapisu pliku
        """
        temp_zip_file = open(save_path, 'wb')
        while 1:
            packet = http_file_obj.read()
            if not packet:
                break
            temp_zip_file.write(packet)
        temp_zip_file.close()
    
    def reset(self):
        super(Napisy24, self).reset()
        self.media_name= None
    
if __name__ == '__main__':
    
    
    file_name = []
    ext_video = ['.avi', '.3gp', '.asf', '.asx', '.divx', '.mkv', '.mov', '.mp4', '.mpeg', '.mpg', '.ogm', '.qt', '.rm', '.rmvb', '.wmv', '.xvid']
    movie_dir = '/media/ork_storage/filmy'
    tv_dir = '/media/ork_storage/tv'
    file_path = '/media/ork_storage/tv/Sherlock.2x01.A.Scandal.In.Belgravia.720p.HDTV.x264-FoV.mkv'
    file_path_1 = '/media/ork_storage/filmy/The Imaginarium of Doctor Parnassus/The.Imaginarium.of.Doctor.Parnassus.DVDRip.XviD-ALLiANCE-CD2.(osloskop.net).avi'
    movie_dir = tv_dir
    pn24 = Napisy24()
    pn24.file_path = file_path
    pn24.get_subs()
    pn24.choice = 1
    pn24.subs_dwn_type = 1
    pn24.download_subs()    