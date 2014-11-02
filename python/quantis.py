#!/usr/bin/python

'''
- author Victor Torre (aka ehooo) https://github.com/ehooo

Hace uso de GTK http://www.pygtk.org/ para mostra un icono en la barra de tareas en caso de hacer uso de esta opcion
'''
import logging
import sqlite3
import httplib
import socket
import urllib
import time
import re
import os
from HTMLParser import HTMLParser
from datetime import datetime
from threading import Thread

GTK_ERROR = False
try:
	import gtk
except ImportError:
	GTK_ERROR = True
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

logger = logging.getLogger(__name__)

class QuantisBandwidth(HTMLParser):
	@staticmethod
	def has_class(attrs, value):
		for (key, val) in attrs:
			if key == 'class':
				if value is not None:
					return val == value
				return True
			return False

	def __init__(self):
		HTMLParser.__init__(self)
		self.in_consumo = False
		self.consumo = ""
		self.in_porcentaje = False
		self.porcentaje = ""
		self.cookie = None
		self.user = None
		self.pwd = None
		self.update_callbacks = []

	def add_updater_callback(self, callback):
		self.update_callbacks.append(callback)
	def handle_data(self, data):
		if self.in_consumo:
			self.consumo += data
		if self.in_porcentaje:
			self.porcentaje += data
	def handle_endtag(self, tag):
		if tag.lower() == "span":
			if self.in_consumo:
				self.in_consumo = False
				self.consumo = self.consumo.strip()
				logger.debug("Leido consumo: %s"%self.consumo)
			if self.in_porcentaje:
				self.in_porcentaje = False
				self.porcentaje = self.porcentaje.strip()
				logger.debug("Leido porcentaje: %s"%self.porcentaje)
	def handle_starttag(self, tag, attrs):
		if tag.lower() == "td" and QuantisBandwidth.has_class(attrs, 'tabla_color5'):
			self.in_consumo = True
		if tag.lower() == "span" and QuantisBandwidth.has_class(attrs, 'porcentaje'):
			self.in_porcentaje = True
	def set_auth(self, user, pwd):
		self.user = user
		self.pwd = pwd
	def auth(self):
		self.get_auth(self.user, self.pwd)
	def get_auth(self, user, pwd, header={}):
		logger.debug("Obteniendo AUTH cokkie")
		conn = httplib.HTTPSConnection("www.quantis.es", timeout=30)
		post = urllib.urlencode({
			'_method':'POST',
			'data[Authentication][email]':user,
			'data[Authentication][password]':pwd
		})
		header['Content-Type'] = 'application/x-www-form-urlencoded'
		conn.request("POST", "/spa/authentications/access", post, header)
		res = conn.getresponse()
		location = res.getheader('location', None)
		if location is None:
			raise RuntimeError('Usuario o Clave erroneos')
		self.cookie = res.getheader('set-cookie', ";").split(';')[0]
		conn.close()
		self.update_data()
	def update_data(self, header={}):
		logger.debug("Actualizando datos")
		self.consumo = ""
		self.porcentaje = ""
		if self.cookie is None:
			raise RuntimeError('Sesion no iniciada')

		conn = httplib.HTTPSConnection("www.quantis.es", timeout=30)
		header['cookie'] = self.cookie
		logger.debug("Iniciando conexion")
		conn.request("GET", "/spa/clients/bandwidth", headers=header)
		res = conn.getresponse()
		location = res.getheader('location', None)
		if location:
			self.cookie = None
			raise RuntimeError('Sesion expirada')
		cookie = res.getheader('set-cookie', None)
		if cookie:
			self.cookie = cookie.split(';')[0]
			logger.debug("Nueva Cookie detectada")
		logger.debug("Procesando la web")
		self.feed(res.read())
		logger.debug("Llamando a %s callbacks: %s"%(len(self.update_callbacks), self.update_callbacks))
		for callback in self.update_callbacks:
			try:
				#thread.start_new_thread(callback, (self.consumo, self.porcentaje) )
				callback(self.consumo, self.porcentaje)
			except Exception as ex:
				print ex
		conn.close()

class QuoteDB():
	CONSUMO_RE = re.compile('(\d+\.?\d*) (G|M)Bytes')
	PORCIEN_RE = re.compile('(\d+\.?\d*)%')
	TIME_FORMAT = '%y-%m-%d %H:%M:%S.%f'
	def __init__(self, quantis_bandwidth, dbname=None):
		self.quantis_bandwidth = quantis_bandwidth
		self.quantis_bandwidth.add_updater_callback( self.update_db )
		create = False
		filename = ":memory:"
		if dbname is None:
			create = True
		else:
			filename = '%s.db'%(os.path.basename(dbname))
			if not os.path.isfile(filename):
				create = True
		self.filename = filename
		logger.debug('Cargando BD desde %s'%filename)
		self.conn = sqlite3.connect( self.filename )
		if create:
			self.create()

	def create(self):
		logger.debug('Creando la BD')
		c = self.conn.cursor()
		c.execute('CREATE TABLE quote (use REAL, percent REAL, date TEXT)')
		self.conn.commit()
		c.close()

	def update_db(self, consumo, porcentaje):
		#TODO Hacer filtro de consume y porcentaje
		use = -1
		try:
			use = QuoteDB.CONSUMO_RE.search(consumo)
			if use:
				(use, vol) = use.groups()
				logger.debug('Consumo procesado %s %s'%(use, vol))
				if vol!='G':
					use = '0.'+use.replace('.','')
			use = float(use)
		except Exception as ex:
			logger.exception(ex)
			use = -1
		percent = -1
		try:
			percent = QuoteDB.PORCIEN_RE.search(porcentaje)
			if percent:
				(percent, ) = percent.groups()
				logger.debug('Porcentaje procesado %s%%'%(percent))
			else:
				percent = porcentaje.replace('%','')
				logger.warn('Fixed Porcentaje %s%%'%(percent))
			percent = float(percent)
		except Exception as ex:
			logger.exception(ex)
			percent = -1

		logger.debug('Saving data %s, %s on DB'%(use, percent))
		c = self.conn.cursor()
		c.execute( "INSERT INTO quote VALUES (%s,%s,'%s')"%(use, percent, datetime.now().strftime(QuoteDB.TIME_FORMAT)) )
		self.conn.commit()
		c.close()

class QuantisTrayIcon():
	def __init__(self, quantis_bandwidth, db=None, daemon=False, timeout=60):
		if GTK_ERROR:
			raise RuntimeError('GTK no soportado')
		self.tray = None
		self.menu = None
		self.db = db
		self.quantis_bandwidth = quantis_bandwidth
		self.ready = False
		self.quantis_bandwidth.add_updater_callback( self.update_gui )
		self.quantis_bandwidth.auth()
		self.daemon = daemon
		self.timeout = timeout
		self.daemon_thread = None
		self.updating_thread = None
		if self.daemon:
			logger.debug('Lanzando hilo para el demonio')
			self.daemon_thread = Thread(target=self.__daemon)
			self.daemon_thread.daemon = True
			self.daemon_thread.start()
			self.daemon_thread.join(1)
			logger.debug('Demonio corriendo sobre %s'%(self.daemon_thread))
		gtk.main()
		logger.debug('Main Done')
	def __daemon(self):
		logger.debug('Demonio Iniciado')
		while self.daemon:
			time.sleep(self.timeout)
			self.refresh_app()

	def refresh_app(self):
		if not self.updating_thread or not self.updating_thread.is_alive():
			logger.debug('Iniciando hilo de actualizacion')
			self.updating_thread = Thread(target=self.__refresh_app, args=(0,))
			self.updating_thread.start()
			logger.debug('Actualizacion corriendo sobre %s'%(self.updating_thread))
			self.updating_thread.join(5)
			logger.debug('Actualizacion waiting')
			#self.updating_thread.join()
			#logger.debug('Actualizacion done')
		else:
			logger.warn("Esperando actualizacion de los datos")
			if self.updating_thread and self.updating_thread.is_alive():
				self.updating_thread.join(1)

	def __refresh_app(self, loop):
		if loop > 10:
			self.updating_thread = None
			logger.error('No se ha podido actualizar la informacion')
			return
		try:
			try:
				logger.warn("Iniciando la actualizacion intento %s"%(loop))
				self.quantis_bandwidth.update_data()
			except RuntimeError as e:
				logger.exception(e)
				self.quantis_bandwidth.auth()
		except socket.error as ex:
			logger.exception(ex)
			self.__refresh_app(loop+1)


	def set_titulo(self, titulo):
		if self.tray:
			logger.debug('Escribiendo titulo')
			self.tray.set_title( titulo )
			self.tray.set_tooltip( titulo )
			self.tray.set_name( titulo )

	def update_gui(self, consumo, porcentaje):
		if not self.ready:
			logger.debug('Creando el icono')
			self.tray = gtk.StatusIcon()
			self.tray.set_from_file(os.path.join(BASE_DIR,'quantis.ico'))
			self.tray.connect('activate', self.on_click)
			self.ready = True

		self.set_titulo( '%s - %s'%(consumo, porcentaje) )
		self.updating_thread = None

	def close_app(self, data=None):
		logger.debug('Saliendo')
		self.daemon = False
		gtk.main_quit()

	def on_click(self, event):
		self.refresh_app()

if __name__ == "__main__":
	options={}
	try:
		import argparse
		parser = argparse.ArgumentParser(description='Actualiza la ip del servicio dinamico de CDmon.com usando la web o la API')

		parser.add_argument("-u", "--user", dest="user", type=str, help="usuario")
		parser.add_argument("-p", "--password", dest="password", type=str, help="clave")
		parser.add_argument("-d", "--daemon", dest="daemon", action="store_true", help="Hacer permanete la consulta", default=False)
		parser.add_argument("-t", "--timeout", dest="timeout", type=int, help="Tiempo de espera entre consultas", default=1800)
		parser.add_argument("-g", "--gui", dest="gui", action="store_true", help="Mostrar como icono en la barra de tareas", default=False)
		parser.add_argument("-s", "--save", dest="dbname", type=str, help="Alamacena los datos en una base de datos sqlite3", default=None)
		parser.add_argument("--db", dest="dbname", type=str, help="Alias de -s", default=None)

		options = vars(parser.parse_args())
	except:
		from optparse import OptionParser
		parser = OptionParser()

		parser.add_option("-u", "--user", dest="user", type="string", help="usuario")
		parser.add_option("-p", "--password", dest="password", type="string", help="clave")
		parser.add_option("-d", "--daemon", dest="daemon", action="store_true", help="Hacer permanete la consulta", default=False)
		parser.add_option("-t", "--timeout", dest="timeout", type="int", help="Tiempo de espera entre consultas", default=1800)
		parser.add_option("-g", "--gui", dest="gui", action="store_true", help="Mostrar como icono en la barra de tareas", default=False)
		parser.add_option("-s", "--save", dest="dbname", type="string", help="Alamacena los datos en una base de datos sqlite3", default=None)
		parser.add_option("--db", dest="dbname", type="string", help="Alias de -s", default=None)

		(options, args) = parser.parse_args()
		options = vars(options)

	FORMAT = "%(asctime)-15s %(message)s"
	FORMAT = '%(module)s:%(filename)s:%(lineno)s %(funcName)20s() %(levelname)s %(asctime)s "%(message)s"'
	logging.basicConfig(format=FORMAT)
	logger.setLevel(logging.DEBUG)
	#logger.setLevel(logging.INFO)
	def print_update(consumo, porcentaje):
		print consumo, porcentaje
	parser = QuantisBandwidth()
	parser.add_updater_callback(print_update)
	db = None
	if options["dbname"] is not None:
		db = QuoteDB(parser, options["dbname"])
	try:
		parser.set_auth(options["user"], options["password"])
		if options['gui']:
			icon = QuantisTrayIcon(parser, db,  options['daemon'], options['timeout'])
			if db:
				db.close()
			exit()
		parser.get_auth(options["user"], options["password"])
		while options['daemon']:
			time.sleep(options['timeout'])
			try:
				parser.update_data()
			except socket.error as er:
				print er
		if db:
			db.close()
	except RuntimeError as ex:
		print ex

