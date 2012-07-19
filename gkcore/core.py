#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
#       gkcore.convert
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
import imp

def findSubclass(plugin_name, plugin_path, cls):
    """
    Function for seraching given class in 
    """
    imported_module = imp.load_source(plugin_name, plugin_path)
        
    module_dict = imported_module.__dict__
    
    for key, entry in module_dict.items():
        if key == cls.__name__:
            continue
        try:
            if issubclass(entry, cls):
                return entry
        except TypeError:
            continue
        
        
    
def pluginLoad(plugin_dirs, cls):
    """
    Function for loading converting plugins
    @plugin_dirs - list of string, each string represents directory with plugins
    @class_name - name of class for subclassed plugins
    returns plugin list - list
    """
    
    plugins = []
    
    for directory in plugin_dirs:
        for root_path, directory, file_name in os.walk(directory):
            for name in file_name:
                if name.endswith('.py') and not name.startswith('__'):
                    plugin_path = os.path.join(root_path, name)
                    name = os.path.splitext(name)[0]
                    finded_plugin = findSubclass(name, plugin_path, cls)
                    if finded_plugin:
                        plugins.append(finded_plugin)
                    
    return plugins

def pluginInstance(plugin_list):
    """
    Function converting classes of load plugin in
    plugin instancecs
    Return list of instances
    @plugin_list - list of loaded plugin classes
    """
    plugin_instance = []
    
    for plc in plugin_list:
        pli = plc()
        plugin_instance.append(pli)
        
    return plugin_instance
        
                    
                    
                    
                    
            
            