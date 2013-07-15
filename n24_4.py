#!/usr/bin/env python
#-*- coding: utf-8 -*-

# Działa - za każdym razem trzeb zamienić PHPSESSID gdyż się zmienia.

from urllib2 import urlopen, HTTPBasicAuthHandler, build_opener, \
				install_opener, Request, HTTPCookieProcessor
import cookielib
import Cookie

dwn_url = 'http://napisy24.pl/download/sr/69827/'
#dwn_url = 'http://napisy24.pl/logowanie/'

headers = {
	'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:20.0) Gecko/20100101 Firefox/20.0',
	'Host': 'napisy24.pl',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language': 'pl,en-us;q=0.7,en;q=0.3',
	'Accept-Encoding': 'gzip, deflate',
	'Referer': 'http://napisy24.pl/download/sr/69827/',
	'Connection': 'keep-alive',
	'Cookie': 'e061f27c191e2faf3dfb9d59b1927ddf=L7M29fn1djf3JbI0uN_V8QpTf9q16NK3QVF62ThxzpTy0H7dLPIliVHUDv_38Lyr; PHPSESSID=dRuqKxwTaFaUHoIMFyX-yoTwTNFF4qbg5iXGgEyzzCWm98bXM6NfgLDEuCg8s6-V',
}

r = Request(dwn_url,headers=headers)

req = urlopen(r)
inf = req.info()
#res = req.read()

print inf
#print res

temp_zip_file = open('/tmp/testn24.zip', 'wb')
while 1:
	packet = req.read()
	print "r"
	#print packet
	if not packet:
		print "t"
		break
	temp_zip_file.write(packet)
temp_zip_file.close()
