#!/usr/bin/env python
#-*- coding: utf-8 -*-

#       test
#       
#       Copyright 2014 Daniel 'yp2' Dereziński <daniel.derezinski@gmail.com> 
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
from gkcore.convert import ConvertBase
from gkcore.core import pluginLoad
from gkcore.subsdwn import SubsDownloadBase

import plugins

print plugins.PLUGINS_CONVERT
print plugins._plugins_convert

class PluginLoadTest(unittest.TestCase):
    def setUp(self):
        self.plugindir0 = [os.getcwd() + '/plugins']
        self.plugindir1 = [os.getcwd() + '/blabla']
        self.plugindir2 = [os.getcwd() + '/gkcore']
        self.plugindir3 = ['/etc/']
        self.plugindir4 = [os.path.expandvars('~')]
        self.plugindir5 = [os.path.expandvars('~/dokumenty')]
        
        
class ConvertPluginLoadTest(PluginLoadTest):
    def setUp(self):
        super(ConvertPluginLoadTest, self).setUp()
        self.plugin_baseclass = ConvertBase
    def test_LoadPlugins_dir0(self):
        "Dir with plugins"
        loaded_plugins = pluginLoad(self.plugindir0, self.plugin_baseclass)
        self.assertEqual(len(loaded_plugins), 4, "Plugins count different from expected")
        self.assertNotEqual(len(loaded_plugins), 0, "No plugin has been loaded")
    def test_LoadPlugins_dir1(self):
        "Dir without plugins"
        loaded_plugins = pluginLoad(self.plugindir1, self.plugin_baseclass)
        self.assertEqual(len(loaded_plugins), 0, "Some plugin has been loaded")
    def test_LoadPlugins_dir2(self):
        "Dir without plugins"
        loaded_plugins = pluginLoad(self.plugindir2, self.plugin_baseclass)
        self.assertEqual(len(loaded_plugins), 0, "Some plugin has been loaded")
    def test_LoadPlugins_dir3(self):
        "Dir without plugins"
        loaded_plugins = pluginLoad(self.plugindir3, self.plugin_baseclass)
        self.assertEqual(len(loaded_plugins), 0, "Some plugin has been loaded")
    def test_LoadPlugins_dir4(self):
        "Dir without plugins"
        loaded_plugins = pluginLoad(self.plugindir4, self.plugin_baseclass)
        self.assertEqual(len(loaded_plugins), 0, "Some plugin has been loaded")
    def test_LoadPlugins_dir5(self):
        "Dir without plugins"
        loaded_plugins = pluginLoad(self.plugindir1, self.plugin_baseclass)
        self.assertEqual(len(loaded_plugins), 0, "Some plugin has been loaded")

class SubsDownloadPluginLoadTest(PluginLoadTest):
    def setUp(self):
        super(SubsDownloadPluginLoadTest, self).setUp()
        self.plugin_baseclass = SubsDownloadBase
    def test_LoadPlugins_dir0(self):
        "Dir with plugins"
        loaded_plugins = pluginLoad(self.plugindir0, self.plugin_baseclass)
        self.assertEqual(len(loaded_plugins), 2, "Plugins count different from expected")
        self.assertNotEqual(len(loaded_plugins), 0, "No plugin has been loaded")
    def test_LoadPlugins_dir1(self):
        "Dir without plugins"
        loaded_plugins = pluginLoad(self.plugindir1, self.plugin_baseclass)
        self.assertEqual(len(loaded_plugins), 0, "Some plugin has been loaded")
    def test_LoadPlugins_dir2(self):
        "Dir without plugins"
        loaded_plugins = pluginLoad(self.plugindir2, self.plugin_baseclass)
        self.assertEqual(len(loaded_plugins), 0, "Some plugin has been loaded")
    def test_LoadPlugins_dir3(self):
        "Dir without plugins"
        loaded_plugins = pluginLoad(self.plugindir3, self.plugin_baseclass)
        self.assertEqual(len(loaded_plugins), 0, "Some plugin has been loaded")
    def test_LoadPlugins_dir4(self):
        "Dir without plugins"
        loaded_plugins = pluginLoad(self.plugindir4, self.plugin_baseclass)
        self.assertEqual(len(loaded_plugins), 0, "Some plugin has been loaded")
    def test_LoadPlugins_dir5(self):
        "Dir without plugins"
        loaded_plugins = pluginLoad(self.plugindir1, self.plugin_baseclass)
        self.assertEqual(len(loaded_plugins), 0, "Some plugin has been loaded")
        
