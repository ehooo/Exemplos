#!/usr/bin/python

'''
- author Victor Torre (aka ehooo) https://github.com/ehooo

chmod a+x /usr/lib/nagios/plugins/check_mongo.py
 'check_mongo' command definition
define command{
	command_name	check_mongodb
	command_line	/usr/lib/nagios/plugins/check_mongo.py -H $HOSTADDRESS$
}
define command {
	command_name	check_mongodb_auth
	command_line	/usr/lib/nagios/plugins/check_mongo.py -H $HOSTADDRESS$ -u $ARG1$ -p $ARG2$
}
define command{
	command_name	check_mongodb_port
	command_line	/usr/lib/nagios/plugins/check_mongo.py -H $HOSTADDRESS$ -P $ARG1$
}
define command {
	command_name	check_mongodb_auth_port
	command_line	/usr/lib/nagios/plugins/check_mongo.py -H $HOSTADDRESS$ -u $ARG1$ -p $ARG2$ -P $ARG3$
}
'''

import os
import shlex
import subprocess

class Mongo_Plugin():
	def __init__(self, host='localhost', port=None, db=None, user=None, password=None):
		if not port:
			port = 27017
		self.cmd = 'mongostat -h %(host)s:%(port)s -n 1  --noheaders' % {
			"port":port,
			"host":host
		}
		if db and mode != "mongo":
			self.cmd += "%s"%db
		if user:
			self.cmd += " -u %s"%user
		if password:
			self.cmd += " -p %s"%password

	def run(self):
		response = "CRITICAL"
		ret_code = 2
		flushes = -1
		locked = -1
		conn = -1
		#TODO Detectar error de conexion
		cmd_ = subprocess.Popen(shlex.split(self.cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		if True:
			cmd = "grep -v connected"
			grep = subprocess.Popen(shlex.split(cmd.encode('ascii')), stdin=cmd_.stdout,  stdout=subprocess.PIPE)
			grep.wait()
			line = grep.stdout.read()
			cmd_.wait()
			

			cmd = "awk '{print $6}'"
			awk = subprocess.Popen(shlex.split(cmd.encode('ascii')), stdin=subprocess.PIPE,  stdout=subprocess.PIPE)
			(command, stderrdata) = awk.communicate(line)
			awk.wait()

			cmd = "awk '{print $7}'"
			awk = subprocess.Popen(shlex.split(cmd.encode('ascii')), stdin=subprocess.PIPE,  stdout=subprocess.PIPE)
			(flushes, stderrdata) = awk.communicate(line)
			awk.wait()

			cmd = "awk '{print $12}'"
			awk = subprocess.Popen(shlex.split(cmd.encode('ascii')), stdin=subprocess.PIPE,  stdout=subprocess.PIPE)
			(locked, stderrdata) = awk.communicate(line)
			awk.wait()

			cmd = "awk '{print $18}'"
			awk = subprocess.Popen(shlex.split(cmd.encode('ascii')), stdin=subprocess.PIPE,  stdout=subprocess.PIPE)
			(conn, stderrdata) = awk.communicate(line)
			awk.wait()

			if cmd_.returncode == 0:
				response = "OK"
				ret_code = 0
			else:
				response += " %s" % cmd_.stderr.read()
				

		flushes = flushes.replace('\n','').replace('\r','')
		locked = locked.replace('\n','').replace('\r','')
		conn = conn.replace('\n','').replace('\r','')
		text = "%(response)s flushes:%(flushes)s locked:%(locked)s conn:%(conn)s" % {
			'response':response,
			'flushes':flushes,
			'locked':locked,
			'conn':conn
		}
		return ret_code, "%(text)s | flushes=%(flushes)s;;;0; locked=%(locked)s;;;0; conn=%(conn)s;;;0; " % {
			'text':text,
			'flushes':flushes,
			'locked':locked,
			'conn':conn
		}

if __name__ == "__main__":
	options={}
	try:
		import argparse

		parser = argparse.ArgumentParser(description='Mongo monitor for Nagios.')

		parser.add_argument("-H", "--host", dest="host", type=str,
						  help="Mongo server", default='localhost')
		parser.add_argument("-P", "--port", dest="port", type=int, action="store",
						  help="Mongo port [default: %(default)i]", default=27017, metavar="NUM")

		parser.add_argument("-u", "--user", dest="user", type=str, help="Mongo user")
		parser.add_argument("-p", "--password", dest="password", type=str, help="Mongo password")
		parser.add_argument("-D", "--db", dest="db", type=str, help="Mongo db name")

		options = vars(parser.parse_args())
	except:
		from optparse import OptionParser

		parser = OptionParser()

		parser.add_option("-H", "--host", dest="host", type="string",
						  help="Mongo server", default='localhost')
		parser.add_option("-P", "--port", dest="port", type="int", action="store",
						  help="Mongo port [default: %(default)i]", default=27017, metavar="NUM")

		parser.add_option("-u", "--user", dest="user", type="string", help="Mongo user")
		parser.add_option("-p", "--password", dest="password", type="string", help="Mongo password")
		parser.add_option("-D", "--db", dest="db", type="string", help="Mongo db name")

		(options, args) = parser.parse_args()
		options = vars(options)

	plug = Mongo_Plugin(options["host"], options["port"], options["db"], options["user"], options["password"])
	ret, text =  plug.run()
	print text
	exit(ret)