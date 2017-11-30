from serial import Serial
from serial.tools.list_ports import comports as ports
import logging, os

#from settings import *

# if __name__ == '__main__':
from adapterctl.__init__ import *
# else:
# 	from __main__ import *

# logging.basicConfig(format='[%(asctime)s - %(name)s - %(levelname)s] %(message)s', filename=os.path.join(TMP_DIR, LOG_FILE))

log = get_logger('USB')
out_log = log.getChild('send')
in_log = log.getChild('receive')



class Connection():
	def __init__(self):
		self.port = self.get_port()
		self.serial = Serial(self.port, 9600, timeout=0.1)
		log.info('Preparing connection')
		self.get_response()

	def get_response(self):
		for n in range(20):
			response = self.serial.readline()
			if response:
				return response
		else:
			return None

	def send(self, pin, status):
		pin = str(pin)
		pinid = '0' * (PINID_LENGHT - len(pin)) + pin
		send = 'PIN' + pinid + '=' + str(status) + '\n'
		self.serial.write(send.encode('utf-8'))
		response = self.get_response()
		out_log.info(send.replace('\n', ''))
		in_log.debug(response.decode().replace('\n', ''))

	def get_port(self):
		print(ports())
		for p in ports():
			print(p.device)
			if MANUFACTURER in p.manufacturer:
				return p.device
				break

if __name__ == '__main__':
	con = Connection()
	con.send(2, 0)
	con.send(3, 0)
	con.send(4, 1)
