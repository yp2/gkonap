#!/usr/bin/env python
#-*- coding: utf-8 -*-

import urllib2
import cookielib

theurl = 'http://napisy24.pl/logowanie/'
username = 'yp26'
password = 'daniel26'
# a great password

passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
# this creates a password manager
passman.add_password(None, theurl, username, password)
# because we have put None at the start it will always
# use this username/password combination for  urls
# for which `theurl` is a super-url

authhandler = urllib2.HTTPBasicAuthHandler(passman)
# create the AuthHandler
cj = cookielib.CookieJar()
cookie = urllib2.HTTPCookieProcessor(cj)

opener = urllib2.build_opener(authhandler, cookie)
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

urllib2.install_opener(opener)
# All calls to urllib2.urlopen will now use our handler
# Make sure not to include the protocol in with the URL, or
# HTTPPasswordMgrWithDefaultRealm will be very confused.
# You must (of course) use it when fetching the page though.

pagehandle = urllib2.urlopen(theurl)
# authentication is now handled automatically for us
print pagehandle.info()
print pagehandle.geturl()
