#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
#       test
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

import os
import unittest
try:
    from cdecimal import Decimal
except ImportError:
    from decimal import Decimal
    
from gkcore.core import pluginLoad, pluginInstance
from gkcore.convert import ConvertBase
import gkcore.info
import plugins


class PluginLoadTest(unittest.TestCase):
    def setUp(self):
        plugindir1 = os.getcwd() + '/plugins'
        self.plugins_dir = [plugindir1]
    
class ConvertPluginLoadTest(PluginLoadTest):
    def setUp(self):
        PluginLoadTest.setUp(self)
        self.plugin_subclass_convert = ConvertBase
    def test_loadConvertPlugins(self):
        loaded_plugins = pluginLoad(self.plugins_dir, self.plugin_subclass_convert)
        self.assertNotEqual(len(loaded_plugins), 0, "Plugins not Loaded")
    def test_doInstanceConvertPlugins(self):
        loaded_plugins_classes = pluginLoad(self.plugins_dir, self.plugin_subclass_convert)
        loaded_plugins_instances = []
        for plc in loaded_plugins_classes:
            plugin_instance = plc()
            loaded_plugins_instances.append(plugin_instance)
        self.assertNotEqual(len(loaded_plugins_instances), 0, "No Plugin Instance")
        
class ConvertPluginRecognizeTest(PluginLoadTest):
    def setUp(self):
        PluginLoadTest.setUp(self)
        # load and do instances of plugns
        plugins = pluginLoad(self.plugins_dir, ConvertBase)
        self.plugins = pluginInstance(plugins)
        # subtitles files
        self.test_files_dir = os.getcwd() + '/test_files/'
        self.sub_mdvd = self.test_files_dir + 'mdvd.txt'
        self.sub_mpl2 = self.test_files_dir + 'mpl2.txt'
        self.sub_srt = self.test_files_dir + 'srt.srt'
        self.sub_tmpl = self.test_files_dir + 'tmpl.txt'
        self.not_sub = self.test_files_dir + 'notsub.txt'
        
    def test_mdvdRecognize(self):
        given_subs_type = 'mdvd'
        sub_file = self.sub_mdvd
        
        subs_type = []
        
        for pli in self.plugins:
            try:
                st = pli.recognize(sub_file)
            except (TypeError, NotImplementedError):
                continue
            
            if st != None:
                subs_type.append(st)
                
        self.assertEqual(len(subs_type), 1, "More than one or zero")
        self.assertEqual(subs_type[0], given_subs_type, 'Not recognize')
    
    def test_mpl2Recognize(self):
        given_subs_type = 'mpl2'
        sub_file = self.sub_mpl2
        
        subs_type = []
        
        for pli in self.plugins:
            try:
                st = pli.recognize(sub_file)
            except (TypeError, NotImplementedError):
                continue
            
            if st != None:
                subs_type.append(st)
                
        self.assertEqual(len(subs_type), 1, "More than one or zero")
        self.assertEqual(subs_type[0], given_subs_type, 'Not recognize')
    
    def test_srtRecognize(self):
        given_subs_type = 'srt'
        sub_file_path = self.sub_srt
                
        subs_type = []
        
        for pli in self.plugins:
            try:
                st = pli.recognize(sub_file_path)
            except (TypeError, NotImplementedError):
                continue
            
            if st != None:
                subs_type.append(st)
        
        self.assertEqual(len(subs_type), 1, "More than one or zero")
        self.assertEqual(subs_type[0], given_subs_type, 'Not recognize')
    
    def test_tmplRecognize(self):
        given_subs_type = 'tmpl'
        sub_file = self.sub_tmpl
        
        subs_type = []
        
        for pli in self.plugins:
            try:
                st = pli.recognize(sub_file)
            except (TypeError, NotImplementedError):
                continue
            
            if st != None:
                subs_type.append(st)
                
        self.assertEqual(len(subs_type), 1, "More than one or zero")
        self.assertEqual(subs_type[0], given_subs_type, 'Not recognize')
    
    def test_noSubsFileRecognize(self):
        sub_file = self.not_sub
        
        subs_type = []
        
        for pli in self.plugins:
            try:
                st = pli.recognize(sub_file)
            except (TypeError, NotImplementedError):
                continue
            
            if st != None:
                subs_type.append(st)
                
        self.assertEqual(len(subs_type), 0, "No subs file was recognize as subs file")


        
class DecomposeTest(ConvertPluginRecognizeTest):
    def setUp(self):
        ConvertPluginRecognizeTest.setUp(self)
        self.first_line = [Decimal('0.041'), Decimal('3.003'), 'movie info: XVID  720x304 23.976fps 367.6 MB|SubEdit b.4072 (http://subedit.com.pl)']
        self.middle_line = [Decimal('5426.468'), Decimal('5428.887'), 'Pomna\xbfa armi\xea|w lochach Isengardu.']
        self.last_line = [Decimal('12050.717'), Decimal('12053.720'), '.:: Napisy24 - Nowy Wymiar Napis\xf3w ::.|Napisy24.pl']
        
        
        self.tmpl_first_line = [Decimal('0.0'), Decimal('6.0'), 'movie info: XVID  720x304 23.976fps 367.6 MB|SubEdit b.4072 (http://subedit.com.pl)']
        self.tmpl_middle_line = [Decimal('5427.0'), Decimal('5429.0'), 'Pomna\xbfa armi\xea|w lochach Isengardu.']
        self.tmpl_last_line = [Decimal('12051.0'), Decimal('12053.0'), '.:: Napisy24 - Nowy Wymiar Napis\xf3w ::.|Napisy24.pl']
        
        
        self.line_list = [self.first_line, self.middle_line, self.last_line]
        self.tmpl_line_list = [self.tmpl_first_line, self.tmpl_middle_line, self.tmpl_last_line]
        
        self.line_decompose_number = [0, 866, -1]
        
    def test_srtDecompose(self):
        subs_path = self.sub_srt
        movie_fps = 23.976
        #recognize and processing
        for pli in self.plugins:
            if pli.recognize(subs_path):
                pli.decompose(subs_path, movie_fps)
                decompose_subs = pli.decomposed_subtitle
        
        self.assertNotEqual(decompose_subs, None, "No decompose subs")
        
        for y in range(3):
            self.assertEqual(decompose_subs[self.line_decompose_number[y]][2], self.line_list[y][2])
            for x in range(2):
                #for times tests
                self.assertEqual(decompose_subs[self.line_decompose_number[y]][x], self.line_list[y][x])
            

#        self.assertEqual(decompose_subs[0], self.first_line, 'Fail First line')
#        self.assertEqual(decompose_subs[866], self.middle_line, 'Fail Middle line')
#        self.assertEqual(decompose_subs[-1], self.last_line, 'Fail Last line')
    
    def test_mdvdDecompose(self):
        subs_path = self.sub_mdvd
        movie_fps = 23.976
        #recognize and processing
        for pli in self.plugins:
            if pli.recognize(subs_path):
                pli.decompose(subs_path, movie_fps)
                decompose_subs = pli.decomposed_subtitle
        
        self.assertNotEqual(decompose_subs, None, "No decompose subs")
        
        for y in range(3):
            self.assertEqual(decompose_subs[self.line_decompose_number[y]][2], self.line_list[y][2])
            for x in range(2):
                #for times tests
                self.assertAlmostEqual(decompose_subs[self.line_decompose_number[y]][x], self.line_list[y][x], places=2)
            
        
#        self.assertEqual(decompose_subs[0], self.first_line, 'Fail First line')
#        self.assertEqual(decompose_subs[-1], self.last_line, 'Fail Last line')
#        self.assertEqual(decompose_subs[866], self.middle_line, 'Fail Middle line')

    def test_mpl2Decompose(self):
            subs_path = self.sub_mpl2
            movie_fps = 23.976
            #recognize and processing
            for pli in self.plugins:
                if pli.recognize(subs_path):
                    pli.decompose(subs_path, movie_fps)
                    decompose_subs = pli.decomposed_subtitle
            
            self.assertNotEqual(decompose_subs, None, "No decompose subs")
            
            for y in range(3):
                self.assertEqual(decompose_subs[self.line_decompose_number[y]][2], self.line_list[y][2])
                for x in range(2):
                    #for times test mpl2 is less acurate than mdvd, srt
                    self.assertAlmostEqual(decompose_subs[self.line_decompose_number[y]][x], self.line_list[y][x], places=0)
    
    def test_tmplDecompose(self):
            subs_path = self.sub_tmpl
            movie_fps = 23.976
            #recognize and processing
            for pli in self.plugins:
                if pli.recognize(subs_path):
                    pli.decompose(subs_path, movie_fps)
                    decompose_subs = pli.decomposed_subtitle
            
            self.assertNotEqual(decompose_subs, None, "No decompose subs")
            
            for y in range(3):
                self.assertEqual(decompose_subs[self.line_decompose_number[y]][2], self.tmpl_line_list[y][2])
                for x in range(2):
                    #for times test tmpl is less acurate than mdvd, srt
                    self.assertEqual(decompose_subs[self.line_decompose_number[y]][x], self.tmpl_line_list[y][x])
        
class ComposeTest(ConvertPluginRecognizeTest):
    def setUp(self):
        super(ComposeTest, self).setUp()
        
        self.comp_test_sub_mdvd = self.test_files_dir + 'ct_mdvd.txt'
        self.comp_test_sub_mpl2 = self.test_files_dir + 'ct_mpl2.txt'
        self.comp_test_sub_srt = self.test_files_dir + 'ct_srt.srt'
        self.comp_test_sub_tmpl = self.test_files_dir + 'ct_tmpl.txt'
        self.comp_test_paths = [self.comp_test_sub_mdvd, self.comp_test_sub_mpl2,
                                self.comp_test_sub_srt, self.comp_test_sub_tmpl]
        
    def tearDown(self):
        for path in self.comp_test_paths:
            if os.path.exists(path):
                os.remove(path)
        
    def test_srtCompose(self):
        subs_path = self.sub_srt
        compose_out_path = self.comp_test_sub_srt
        movie_fps = 23.976
        for pli in self.plugins:
            if pli.recognize(subs_path):
                pli.decompose(subs_path, movie_fps)
                decompose_subs = pli.decomposed_subtitle
                
                #assign decopose_subs for pli.decomposed_substitle
                pli.decomposed_subtitle = None
                pli.decomposed_subtitle = decompose_subs
                
                #compose 
                pli.compose(movie_fps)
                
                #write to file
                pli.writeComposeSubs(compose_out_path)
                
        org_subs = open(subs_path, 'rU').readlines()
        conv_subs = open(compose_out_path, 'ru').readlines()
        
        
        self.assertEqual(org_subs, conv_subs, "Pliki nie są identyczne")
        
#        while org_subs:
#            self.assertEqual(org_subs[0], conv_subs[0], 'Linie nie jest identyczna\n%i\n%s')
#            org_subs = org_subs[1:]
#            conv_subs = conv_subs[1:]

    def test_mdvdCompose(self):
        subs_path = self.sub_mdvd
        compose_out_path = self.comp_test_sub_mdvd
        movie_fps = 23.976
        for pli in self.plugins:
            if pli.recognize(subs_path):
                pli.decompose(subs_path, movie_fps)
                decompose_subs = pli.decomposed_subtitle
                
                #assign decopose_subs for pli.decomposed_substitle
                pli.decomposed_subtitle = None
                pli.decomposed_subtitle = decompose_subs
                
                #compose 
                pli.compose(movie_fps)
                
                #write to file
                pli.writeComposeSubs(compose_out_path)
                
        org_subs = open(subs_path, 'rU').readlines()
        conv_subs = open(compose_out_path, 'ru').readlines()
        
        
        self.assertEqual(org_subs, conv_subs, "Pliki nie są identyczne")
        
#        while org_subs:
#            self.assertEqual(org_subs[0], conv_subs[0], 'Linie nie jest identyczna\n%i\n%s')
#            org_subs = org_subs[1:]
#            conv_subs = conv_subs[1:]
    
    def test_mpl2Compose(self):
        subs_path = self.sub_mpl2
        compose_out_path = self.comp_test_sub_mpl2
        movie_fps = 23.976
        for pli in self.plugins:
            if pli.recognize(subs_path):
                pli.decompose(subs_path, movie_fps)
                decompose_subs = pli.decomposed_subtitle
                
                #assign decopose_subs for pli.decomposed_substitle
                pli.decomposed_subtitle = None
                pli.decomposed_subtitle = decompose_subs
                
                #compose 
                pli.compose(movie_fps)
                
                #write to file
                pli.writeComposeSubs(compose_out_path)
                
        org_subs = open(subs_path, 'rU').readlines()
        conv_subs = open(compose_out_path, 'ru').readlines()
        
        
        self.assertEqual(org_subs, conv_subs, "Pliki nie są identyczne")
#        while org_subs:
#            self.assertEqual(org_subs[0], conv_subs[0], 'Linie nie jest identyczna\n%s\n%s' % (org_subs[0], conv_subs[0]) )
#            org_subs = org_subs[1:]
#            conv_subs = conv_subs[1:]

    def test_tmplCompose(self):
        subs_path = self.sub_tmpl
        compose_out_path = self.comp_test_sub_tmpl
        movie_fps = 23.976
        for pli in self.plugins:
            if pli.recognize(subs_path):
                pli.decompose(subs_path, movie_fps)
                decompose_subs = pli.decomposed_subtitle
                
                #assign decopose_subs for pli.decomposed_substitle
                pli.decomposed_subtitle = None
                pli.decomposed_subtitle = decompose_subs
                
                #compose 
                pli.compose(movie_fps)
                
                #write to file
                pli.writeComposeSubs(compose_out_path)
                
        org_subs = open(subs_path, 'rU').readlines()
        conv_subs = open(compose_out_path, 'ru').readlines()
        
        
        self.assertEqual(org_subs, conv_subs, "Pliki nie są identyczne")
#        while org_subs:
#            self.assertEqual(org_subs[0], conv_subs[0], 'Linie nie jest identyczna\n%s\n%s' % (org_subs[0], conv_subs[0]) )
#            org_subs = org_subs[1:]
#            conv_subs = conv_subs[1:]
    

class GetFpsFromFile(unittest.TestCase):
    def setUp(self):
        self.path_avi = '/media/ork_storage/filmy/Fury/Fury (Fritz Lang 1936) Dvdrip Xvid Ac3-c00Ldude.avi'
        self.path_mkv = '/media/ork_storage/tv/Sherlock.2x01.A.Scandal.In.Belgravia.720p.HDTV.x264-FoV.mkv'
        self.path_mp4 = '/media/ork_storage/filmy/Black.Swan/Black.Swan.mp4'
        self.path_blind = '/media/ork_storage/completed/True.Blood.S05E02.720p.HDTV.x264-IMMERSE.srt'
        self.path_list = [self.path_avi, self.path_mkv, self.path_mp4, self.path_blind]
        
        self.fps_avi = Decimal('23.976')
        self.fps_mkv = Decimal('25.000')
        self.fps_mp4 = Decimal('23.976')
        self.fps_blind = None
        self.fps_list = [self.fps_avi, self.fps_mkv, self.fps_mp4, self.fps_blind]
        
    def test_getFps(self):
        "Metoda testuje główna funkcje modułu info.py"
        
        fps_out = []
        
        for path in self.path_list:
            fps = gkcore.info.get_fps(path)
            fps_out.append(fps)
        
        self.assertEqual(self.fps_list, fps_out, "Fps nie są identyczne - get_fps")
    
    #
    # Poniższe testy służa do sprawdzania funkcji 
    # składowych modułu info.py potrzebnych do działania
    # głównej funkcji get_fps
    # 
    def test_fps_mediainfo(self):
        # Funkcja zwraca wszystkie wyniki
        fps_out = []
        for path in self.path_list:
            fps = gkcore.info.fps_mediainfo(path)
            fps_out.append(fps)
        
        self.assertEqual(self.fps_list, fps_out, 'Fps nie jest identyczne - mediainfo')
    
    def test_fps_kaa_metadata(self):
        # Własna definicja poprawności testu.
        # Ta funkcja nie zwraca fps dla plików mp4
        fps_list = [self.fps_avi, self.fps_mkv, None, self.fps_blind]
        fps_out = []
        for path in self.path_list:
            fps = gkcore.info.fps_kaa_metada(path)
            fps_out.append(fps)
        
        self.assertEqual(fps_list, fps_out, "Fps nie jest identyczny - kaa.metadata")
        
    def test_fps_mplayer(self):
        # Mplayer odczytuje fps tak jak należy 
        # porównanie do już zdefiniowanych list w setUp
        fps_out = []
        
        for path in self.path_list:
            fps = gkcore.info.fps_mplayer(path)
            fps_out.append(fps)
        
        self.assertEqual(self.fps_list, fps_out, "Fps nie są identyczne - mplayer")
    
    def test_fps_ffprobe(self):
        # ffprobe jest mniej dokładne
        # Odczytuje wszystkie formaty
        
        fps_avi = Decimal('23.980')
        fps_mkv = Decimal('25.000')
        fps_mp4 = Decimal('23.980')
        fps_list = [fps_avi, fps_mkv, fps_mp4, self.fps_blind]
        fps_out = []
        for path in self.path_list:
            fps = gkcore.info.fps_ffprobe(path)
            fps_out.append(fps)
        
        self.assertEqual(fps_list, fps_out, "Fps nie są identyczne - ffprobe")
        
    def test_fps_file(self):
        # file nie odczytuje wszystkich formatów
        # jest mniej dokładny
        fps_avi = Decimal('23.980')
        fps_mkv = None
        fps_mp4 = None
        fps_list = [fps_avi, fps_mkv, fps_mp4, self.fps_blind]
        fps_out = []
        for path in self.path_list:
            fps = gkcore.info.fps_file(path)
            fps_out.append(fps)
        
        self.assertEqual(fps_list, fps_out, "Fps nie są identyczne - file")
        
#TODO: Dodać testy:
# - rozpoznawania file like object przez convert plugins
# - zamiany rzoszeżenia przy błędnym rozszeżeniu w zależności od typu napisów
# - testy pluginów do pobierania napisów
        