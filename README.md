# Licencia
Copyright (C) 2013 [ehooo](https://github.com/ehooo)

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# Acerca de:
Ejemplos y utiles varios.

# RPi
Ejemplos de acceso a sensores usando [Adafruit_GPIO](https://github.com/adafruit/Adafruit_Python_GPIO)
 * [ADS1x15](rpi/ADS1x15.py) Fork de [Adafruit_ADS1x15](https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/tree/master/Adafruit_ADS1x15)
 * [MPL3115A2](rpi/MPL3115A2.py) Basado en [MPL3115A2_Breakout](https://github.com/sparkfun/MPL3115A2_Breakout)
 * [RainSensor](rpi/RainSensor.py) y [WindSensor](rpi/WindSensor.py) portados de [Weather_Station](https://github.com/ehooo/Weather_Station)

# Processing
Ejemplos de programas para [Processing](http://processing.org/)
 * [SimpleTwitter](processing/SimpleTwitter):
 Es un ejemplo de uso de acceso a [Twitter](https://dev.twitter.com/apps) usando la libreria [oauthP5](http://www.nytlabs.com/oauthp5/)

# Arduino
Ejemplos de para [Arduino](http://arduino.cc/)
 * [Meteo](arduino/Meteo):
 Es un ejemplo de una minima estación meteorilógica.<br/>
 Hace uso de la librería [Adafruit-BMP085](https://github.com/adafruit/Adafruit-BMP085-Library) para el barometro
 de [arduino-DHT](https://github.com/markruys/arduino-DHT) para el sensor de humedad y
 de [Webduino](https://github.com/sirleech/Webduino) para el servidor Ethernet

# Python
Ejemplos/Utilidades en python
* [Check mongo](python/check_mongo.py):
 Pluging para [Nagios](http://www.nagios.org/) que permite monitorizar el estado de un server con [mongoDB](http://www.mongodb.org/)
 ```
 usage: check_mongo.py [-h] [-H HOST] [-P NUM] [-u USER] [-p PASSWORD] [-D DB]

Mongo monitor for Nagios.

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  Mongo server
  -P NUM, --port NUM    Mongo port [default: 27017]
  -u USER, --user USER  Mongo user
  -p PASSWORD, --password PASSWORD
                        Mongo password
  -D DB, --db DB        Mongo db name
 ```
* [Malware unzip](python/malware_unzip.py):
 Utilidad para descomprimir una lista los ficheros .zip con clase 'infected' de una carpeta y guardar su contenido en otra
```
usage: malware_unzip.py [-h] [-u PATH] [-f FILE] [-p PATH] [-P CLAVE]

Compresor de ficheros cifrados

optional arguments:
  -h, --help            show this help message and exit
  -u PATH, --unpath PATH
                        carpeta donde se almancenaran los ficheros
                        descomprimidos
  -f FILE, --file FILE  fichero zip a descomprimir
  -p PATH, --path PATH  Carpeta con ficheros .zip a descomprimir
  -P CLAVE, --password CLAVE
                        Clave para descomprimir los .zip
```
* [CDmon](python/cdmon.py):
 Utilidad para actualizar la IP dinamica del servicio de [CDmon](https://www.cdmon.com/) usando la [web](https://dinamico.cdmon.org) o la [API](https://support.cdmon.com/entries/24118056-API-de-actualizaci%C3%B3n-de-IP-del-DNS-gratis-din%C3%A1mico)
```
usage: cdmon.py [-h] [-u USER] [-p PASSWORD] [-i IP] [-a]

Actualiza la ip del servicio dinamico de CDmon.com usando la web o la API

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  usuario
  -p PASSWORD, --password PASSWORD
                        clave
  -i IP, --ip IP        IP
  -a, --api             Hacer uso de la API
```
* [Quantis](python/quantis.py):
 Utilidad para conocer el uso de datos de un usuario del servicio a internet por satelite de [Quantis](https://www.quantis.es/). Hace uso de pyGTK para mostrar un icono permanete en la barra de tareas.
```
usage: quantis.py [-h] [-u USER] [-p PASSWORD] [-d] [-t TIMEOUT] [-g]
                  [-s DBNAME] [--db DBNAME]

Actualiza la ip del servicio dinamico de CDmon.com usando la web o la API

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  usuario
  -p PASSWORD, --password PASSWORD
                        clave
  -d, --daemon          Hacer permanete la consulta
  -t TIMEOUT, --timeout TIMEOUT
                        Tiempo de espera entre consultas
  -g, --gui             Mostrar como icono en la barra de tareas
  -s DBNAME, --save DBNAME
                        Alamacena los datos en una base de datos sqlite3
  --db DBNAME           Alias de -s
```