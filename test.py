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
from gkcore.core import pluginLoad, pluginInstance
from gkcore.convert import ConvertBase
from plugins.srt import PluginSRT
import unittest
import inspect


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
        self.first_line = [0.041, 3.003, 'movie info: XVID  720x304 23.976fps 367.6 MB\n<i>SubEdit b.4072 (http:<i><i>subedit.com.pl)<i></i>']
        self.last_line = [12050.717, 12053.720, '.:: Napisy24 - Nowy Wymiar Napis\xf3w ::.\nNapisy24.pl\n\n']
        self.middle_line = [5426.468, 5428.887, 'Pomna\xbfa armi\xea\nw lochach Isengardu.']
    
    def test_srtDecompose(self):
        subs_path = self.sub_srt
        movie_fps = 23.976
        #recognize and processing
        for pli in self.plugins:
            if pli.recognize(subs_path):
                pli.decompose(subs_path, movie_fps)
                decompose_subs = pli.decomposed_subtitle
        
        self.assertNotEqual(decompose_subs, None, "No decompose subs")
        self.assertEqual(decompose_subs[0], self.first_line, 'Fail First line')
        self.assertEqual(decompose_subs[-1], self.last_line, 'Fail Last line')
        self.assertEqual(decompose_subs[866], self.middle_line, 'Fail Middle line')
    
    def test_mdvdDecompose(self):
        subs_path = self.sub_mdvd
        movie_fps = 23.976
        #recognize and processing
        for pli in self.plugins:
            if pli.recognize(subs_path):
                pli.decompose(subs_path, movie_fps)
                decompose_subs = pli.decomposed_subtitle
        
        self.assertNotEqual(decompose_subs, None, "No decompose subs")        
        self.assertEqual(decompose_subs[0], self.first_line, 'Fail First line')
        self.assertEqual(decompose_subs[-1], self.last_line, 'Fail Last line')
        self.assertEqual(decompose_subs[866], self.middle_line, 'Fail Middle line')
        
        