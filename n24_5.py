#!/usr/bin/env python
#-*- coding: utf-8 -*-

from urllib2 import urlopen, HTTPBasicAuthHandler, build_opener, \
				install_opener, Request, HTTPCookieProcessor
import cookielib
import Cookie
import urllib
import urllib2
import cPickle

url_log = 'http://napisy24.pl/logowanie/'
dwn_url = 'http://napisy24.pl/download/sr/69827/'
url_n24 = 'http://napisy24.pl/'
url_l = '/logowanie/'


d = {'form_loginZapamietaj': '1',
	'form_logowanieHaslo': 'daniel26',
	'form_logowanieMail': 'yp26',
	'path':	'/logowanie/',
	'postAction': 'sendLogowanie'}

cookiejar = cookielib.CookieJar()
opener = urllib2.build_opener(
    #urllib2.HTTPRedirectHandler(),
    #urllib2.HTTPHandler(debuglevel=0),
    #urllib2.HTTPSHandler(debuglevel=0),
    urllib2.HTTPCookieProcessor(cookiejar),
)

# musi być User-Agent dla normalnej przeglądarki inaczej nie idzie
# pewnie także odpowiedni dla request
h = [#('Content-type', 'application/x-www-form-urlencoded'), 
	#('Content-Length', len(d)), # można użyć len(post_data) i dodać do request później
	('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:20.0) Gecko/20100101 Firefox/20.0'),
	#('Host', 'napisy24.pl'),
	#('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
	#('Accept-Language', 'pl,en-us;q=0.7,en;q=0.3'),
	#('Accept-Encoding', 'gzip, deflate'),
	#('Referer', 'http://napisy24.pl/logowanie/'),
	#('Connection', 'keep-alive'),
	]

opener.addheaders = h

urllib2.install_opener(opener)

data = urllib.urlencode(d)
r = urllib2.urlopen(url_log,data)

# pobranie cookie są w cookiejar
# zapis poszczególnych plików cookie w bazie danych 
# wczytywanie ich z bazy jak nie pójdzie ponownie odświeżenie logowania.
# ponowny zapis do bazy
cs = []

print '\n'
print dir()
for co in cookiejar:
	cs.append(cPickle.dumps(co, cPickle.HIGHEST_PROTOCOL))
print '\n'

# pobieranie napisów

cstr = ''
for ele in cs:
	udele = cPickle.loads(ele)
	cstr = cstr + '%s=%s; ' % (udele.name, udele.value)
	
print cstr
headers = {
	'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:20.0) Gecko/20100101 Firefox/20.0',
	'Host': 'napisy24.pl',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language': 'pl,en-us;q=0.7,en;q=0.3',
	'Accept-Encoding': 'gzip, deflate',
	'Referer': 'http://napisy24.pl/download/sr/69827/',
	'Connection': 'keep-alive',
	'Cookie': cstr,
}

# z openerem nie działa ciekawe czemu
#cj1 = cookielib.CookieJar()
#for ele in cs:
	#cj1.set_cookie(cPickle.loads(ele))
	
#opd = urllib2.build_opener(
	#urllib2.HTTPRedirectHandler(),
    #urllib2.HTTPHandler(debuglevel=0),
    #urllib2.HTTPSHandler(debuglevel=0),
	#urllib2.HTTPCookieProcessor(cj1),
#)
#opd.addheaders = h
#urllib2.install_opener(opd)
#reqd = urllib2.urlopen(dwn_url)

rd = Request(dwn_url,headers=headers)
reqd = urlopen(rd)

	


print reqd.info()
print reqd.geturl()
#print r.read()
o_file = open('/tmp/out.html', 'w')
o_file.write(r.read())
o_file.close()

temp_zip_file = open('/tmp/testn24.zip', 'wb')
while 1:
	packet = reqd.read()
	print "r"
	#print packet
	if not packet:
		print "t"
		break
	temp_zip_file.write(packet)
temp_zip_file.close()



