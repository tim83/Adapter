from serial import Serial
from serial.tools.list_ports import comports as ports

import datetime as dt

from settings import *

class Connection():
	def __init__(self):
		self.port = self.get_port()
		self.serial = Serial(self.port, 9600)
		# self.serial.write('INIT'.encode('utf-8'))

	def send(self, pin, msg):
		pin = str(pin)
		pinid = '0' * (PINID_LENGHT - len(pin)) + pin
		send = 'PIN' + pinid + '=' + str(msg) + '\n'
		self.serial.write(send.encode('utf-8'))
		with open(os.path.join(DATA_DIR, LOG_FILE), 'a') as o:
			o.write(str(dt.datetime.now()) + '\tTo Arduino: ' + send)

	def get_port(self):
		for p in ports():
			if MANUFACTURER in p.manufacturer:
				return p.device
				break
