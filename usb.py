from serial import Serial
from serial.tools.list_ports import comports as ports
from settings import *

class Connection():
	def __init__(self):
		self.port = self.get_port()
		self.serial = Serial(self.port.device, 9600)

	def send(self, msg):
		send = PINID + '=' + msg
		self.serial.write(send.encode('utf-8'))

	def get_port(self):
		for p in ports():
			if MANUFACTURER in p.manufacturer:
				return p
				break
