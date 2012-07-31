#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
#       gkcore.info
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
#
#
#    UWAGA
# Moduł wymaga do działania:
# Bibiloteki dynamiczne: libmediainfo, libzen (http://mediainfo.sourceforge.net, 
# ppa dla paczek https://launchpad.net/~shiki/+archive/mediainfo/
# python: kaa.metadata, MediaInfoDLL.py (wrapper dla libmediainfo)
#
# programy: ffprobe, mplayer, file, 
#
# pomysł na libmediainfo zaczerniety z subsdownloader
# autorstwa Dawid Bankowski <enigma2subsdownloader at gmail.com>


import kaa.metadata
from subprocess import Popen, PIPE, STDOUT
import re
try:
    from cdecimal import Decimal
except ImportError:
    from decimal import Decimal
    
try:
    from gkcore.MediaInfoDLL import *
    MEDIAINFO = True
except OSError:
    MEDIAINFO = False
    
# Ścieżki do porgramów
MPLAYER = 'mplayer'
FFPROBE = 'ffprobe'
FILE = 'file'

def fps_mediainfo(file_path):
    if MEDIAINFO:
        mediainfo = MediaInfo()
        mediainfo.Open(file_path)
        fps = mediainfo.Get(Stream.Video, 0, "FrameRate")
        if fps:
            fps = Decimal(fps).quantize(Decimal('1.000'))
        else:
            fps = None
        mediainfo.Close()
    else:
        fps = None
    
    return fps
    
    
def fps_kaa_metada(file_path):
    """
    Uzyskanie FPS za pomocą modułu kaa.metadata.
    """
    try:
        kaa_parser = kaa.metadata.parse(file_path)
        fps = kaa_parser.video[0].fps
        if fps:
            # Jeżeli wykryto fps to zamieniamy na decimal - do poprawnego liczenia
            fps = Decimal(str(fps)).quantize(Decimal('1.000')) 
    except AttributeError:
        fps = None
    
    return fps

def fps_mplayer(file_path):
    """
    Funkcja używa mplayer'a do zwrócenia fps
    Uwaga trzeba przepuszczać tylko dobre ścieżki do plików wideo
    """
    
    cmd = [MPLAYER, "-vo", "null", "-ao", "null", "-frames", "0", "-identify", file_path]
    # Wyrażenie regularne dla przeszukania wyniku
    re_fps = re.compile(r"(ID_VIDEO_FPS=)(\d*\.\d*)")
    try:  
        mplayer_info = Popen(cmd, stdout=PIPE, stderr=STDOUT)
        mp_out = str(mplayer_info.communicate()[0])
        fps = re.search(re_fps, mp_out).groups()[1]
        # Zwrócenie wartości w postaci Decimal
        fps = Decimal(fps).quantize(Decimal('1.000'))
    except (OSError, ValueError, AttributeError):
        # Wychwycenie wyjątków pierwsze 2 od Popen, ostatni do re.serarch
        fps = None
       
    return fps

def fps_ffprobe(file_path):
    """
    Funkcja używa ffprobe do zwrócenia fps dla pliku.
    """
    cmd = [FFPROBE, file_path]
    # Wyrażenie regularne dla przeszukania wyniku
    # tbr oznaczenie fps dla pliku wideo
    # ffprobe ma mniejszą dokładność niź mplayer oraz
    # kaa.metadata
    re_fps = re.compile(r'(\d*\.\d*|\d*).tbr')
    try:
        ffprobe_info = Popen(cmd, stdout=PIPE, stderr=STDOUT)
        ffprobe_out = str(ffprobe_info.communicate()[0])
        fps = re.search(re_fps, ffprobe_out).groups()[0]
        # Zwrócenie wartości w postaci Decimal
        fps = Decimal(fps).quantize(Decimal('1.000'))
    except (OSError, ValueError, AttributeError):
        # Wychwycenie wyjątków 2 pierwsze dla Popen, ostatni dla re.search
        fps = None  # Zwracamy None jeżeli nie udało znaleźć się fps
    
    return fps

def fps_file(file_path):
    """
    Uzyskanie fps przy wykorzystaniu programu file
    """
    
    cmd = [FILE, file_path]
    # Wyrażenie regularne dla przeszukania wyniku
    re_fps = re.compile(r'(\d*\.\d*).fps')
    try:
        file_info = Popen(cmd, stdout=PIPE, stderr=STDOUT)
        file_out = str(file_info.communicate()[0])
        fps = re.search(re_fps, file_out).groups()[0]
        # Zwrócenie wartości w postaci Decimal
        fps = Decimal(fps).quantize(Decimal('1.000'))
    except (OSError, ValueError, AttributeError):
        # Wychwycenie wyjątków pierwsze 2 od Popen, ostatni do re.serarch
        fps = None
    
    return fps
    
def get_fps(file_path):
    """
    Funkcja zwraca fps dla danego pliku video, lub None
    jeżli nie udało znaleźć fps dla podanego pliku.
    """
    # sprawdzenia zaczynamy od najprostszych metod oraz
    # od jak najbardziej dokładnych
       
    # lista referencji do funkcij
    func_fps = [fps_kaa_metada,
                fps_mplayer,
                fps_mediainfo,
                fps_ffprobe,
                fps_file]

    #dla każdej funkcji sprawdzamy wynik, jeżeli różny
    #od None zwracamy wartość i wyskakujemy z pętli
    for f in func_fps:
        _f_fps = f(file_path)
        if _f_fps != None:
            fps = _f_fps
            break
        fps = _f_fps
    
    return fps


if __name__ == "__main__":
    avi = "/media/ork_storage/tv/MacGyver.Complete.S01.DVDRip.XviD_MEDiEVAL/MacGyver.S01E01.Pilot.DVDRip.XviD-MEDiEVAL.avi"
    mkv = "/media/ork_storage/tv/Sherlock.2x01.A.Scandal.In.Belgravia.720p.HDTV.x264-FoV.mkv"
    mp4 = "/media/ork_storage/filmy/Black.Swan/Black.Swan.mp4"
    blind = "/media/ork_storage/completed/True.Blood.S05E02.720p.HDTV.x264-IMMERSE.srt"
    
    
    file_path = [avi, mkv, mp4, blind]
    for path in file_path:
        print get_fps(path)
    