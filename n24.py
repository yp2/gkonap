#!/usr/bin/env python
#-*- coding: utf-8 -*-

from urllib2 import urlopen, HTTPBasicAuthHandler, build_opener, \
				install_opener, Request
import urllib

url_log = 'http://napisy24.pl/logowanie/'
url_n24 = 'http://napisy24.pl/'
url_l = '/logowanie/'
d = {'form_loginZapamietaj': '1',
	'form_logowanieHaslo': 'daniel26',
	'form_logowanieMail': 'yp26',
	'path':	'/',
	'postAction': 'sendLogowanie'}
	# form id ???

data = urllib.urlencode(d)
print data
#data = data.encode('utf-8')

headers = {
	'Content-Length': '109',
	'Content-type', 'application/x-www-form-urlencoded',
	'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:20.0) Gecko/20100101 Firefox/20.0',
	'Host': 'napisy24.pl',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language': 'pl,en-us;q=0.7,en;q=0.3',
	'Accept-Encoding': 'gzip, deflate',
	'Referer': 'http://napisy24.pl/logowanie/',
	'Connection': 'keep-alive'
}

req = Request(url_log, data, headers, url_log, True )
response = urlopen(req)
print response.info()
the_page = response.read()
o_file = open('/tmp/out.html', 'w')
o_file.write(the_page)
o_file.close()
#auto_handler = HTTPBasicAuthHandler()
#auto_handler.add_password(realm='n24.pl',uri='n24.pl',user='yp26', passwd='daniel26')
#opener = build_opener(auto_handler)
#install_opener(opener)
#urlopen('http://napisy24.pl/logowanie/')
#http_file_obj = urlopen('http://napisy24.pl/download/sr/69827/')
#print http_file_obj

#temp_zip_file = open('/tmp/testn24.zip', 'wb')
#while 1:
	#packet = http_file_obj.read()
	#print packet
	#if not packet:
		#print "t"
		#break
	#temp_zip_file.write(packet)
#temp_zip_file.close()
