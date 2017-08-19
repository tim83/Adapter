#! /usr/bin/python2

from serial import Serial
from serial.tools.list_ports import comports as ports

import datetime as dt
from settings import *

class Connection():
	def __init__(self):
		self.port = self.get_port()
		self.serial = Serial(self.port, 9600, timeout = 0.1)
		self.get_response()

	def get_response(self):
		for n in range(0, 50):
			response = self.serial.readline()
			if response:
				return response
		return 'NO RESPONSE'

	def send(self, pin, status):
		send = 'PIN0' + str(pin) + '=' + str(status) + '\n'
		self.serial.write(send)
		print send
		print self.get_response()
		with open(os.path.join(DATA_DIR, LOG_FILE), 'a') as o:
			o.write(str(dt.datetime.now()) + '\tTo Arduino: ' + send)
		#	if response:
		#		o.write(str(dt.datetime.now()) + '\tFrom Arduino: ' + response)

	def get_port(self):
		for p in ports():
			if MANUFACTURER in p.manufacturer:
				return p.device
				break

if __name__ == '__main__':
	con = Connection()
	con.send(2, 0)
	con.send(3, 0)
	con.send(4, 1)