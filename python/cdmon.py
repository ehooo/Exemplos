#!/usr/bin/python

'''
- author Victor Torre (aka ehooo) https://github.com/ehooo
'''
import httplib, urllib, hashlib
from HTMLParser import HTMLParser

class CdMonDinamicIP(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.ip = None
		self.msg = None
	def handle_data(self, data):
		if self.msg is True:
			self.msg = data
	def handle_starttag(self, tag, attrs):
		if not self.msg and tag.lower() == "div":
			for (key, val) in attrs:
				if key.lower() == "id" and val=="msg":
					self.msg = True
		if not self.ip and tag.lower() == "input":
			safe = False
			ip = None
			for (key, val) in attrs:
				if key.lower() == "name" and val=="ip":
					safe = True
				if key.lower() == "value":
					ip = val
				if ip and safe:
					self.ip = ip
					break

def update_web_ip(user, pwd, cip=None, header={}):
	post = {
		'usuario':user,
		'contrasenya':pwd
	}
	conn = httplib.HTTPSConnection("dinamico.cdmon.org")
	if cip:
		post['ip']=cip
	else:
		conn.request("GET", "/", None, header)
		res = conn.getresponse()
		cip = CdMonDinamicIP()
		cip.feed(res.read())
		print "Nueva IP", cip.ip
		post['ip'] = cip.ip

	header['Content-Type'] = 'application/x-www-form-urlencoded'
	post = urllib.urlencode(post)
	conn.request("POST", "/", post, header)
	res = conn.getresponse()
	cip = CdMonDinamicIP()
	cip.feed(res.read())
	conn.close()
	return cip.msg

def update_api_ip(user, pwd, cip=None, header={}):
	post = {
		'enctype':'MD5',
		'n':user,
		'p':hashlib.md5(pwd).hexdigest()
	}
	if cip:
		post['cip']=cip
	post = urllib.urlencode(post)
	conn = httplib.HTTPSConnection("dinamico.cdmon.org")
	conn.request("GET", "/onlineService.php?%s"%post, {}, header)
	res = conn.getresponse()
	contenido = None
	contenido = res.read()
	ret = {}
	if res.status == httplib.OK:
		contenido = contenido[1:-1]
		for part in contenido.split('&'):
			(key, val) = part.split('=')
			ret[key] = val
	conn.close()
	return ret

if __name__ == "__main__":
	options={}
	try:
		import argparse

		parser = argparse.ArgumentParser(description='Actualiza la ip del servicio dinamico de CDmon.com usando la web o la API')

		parser.add_argument("-u", "--user", dest="user", type=str, help="usuario")
		parser.add_argument("-p", "--password", dest="password", type=str, help="clave")
		parser.add_argument("-i", "--ip", dest="ip", type=str, help="IP", default=None)
		parser.add_argument("-a", "--api", dest="api", action="store_true", help="Hacer uso de la API", default=False)

		options = vars(parser.parse_args())
	except:
		from optparse import OptionParser

		parser = OptionParser()

		parser.add_option("-u", "--user", dest="user", type="string", help="usuario")
		parser.add_option("-p", "--password", dest="password", type="string", help="clave")
		parser.add_option("-i", "--ip", dest="ip", type="string", help="IP", default=None)
		parser.add_option("-a", "--api", dest="api", action="store_true", help="Hacer uso de la API", default=False)

		(options, args) = parser.parse_args()
		options = vars(options)

	if options['api']:
		print update_api_ip(options["user"], options["password"], options['ip'])
	else:
		print update_web_ip(options["user"], options["password"], options['ip'])

