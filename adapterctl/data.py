#! /usr/bin/python3

import datetime as dt
from serial.serialutil import SerialException
from ast import literal_eval
import os, time, psutil, sys, logging

if __name__ == '__main__':
	from adapterctl.__init__ import *
else:
	from __main__ import *
from adapterctl.usb import Connection

# logging.basicConfig(format='[%(asctime)s - %(name)s - %(levelname)s] %(message)s', filename=os.path.join(TMP_DIR, LOG_FILE))
# log = logging.getLogger('data')
log = cfg.get_logger('data')

# if DEBUG:
# 	log.level = logging.DEBUG
# elif VERBOSE:
# 	log.level = logging.INFO

files = os.listdir(cfg.DATA_PATH)
for file in files:
	if "BAT" in file:
		cfg.DATA_PATH = os.path.join(cfg.DATA_PATH, file)

class Battery():
	def __init__(self, linux=True):
		log.info('Starting data')
		self.connection = Connection()
		self.linux = linux

		os.makedirs(cfg.TMP_DIR, exist_ok=True)

		self.charge = cfg.charge
		self.set_charge()

	def get_data(self):
		self.data = {}

		self.data['charging'] = psutil.sensors_battery().power_plugged
		self.data['percent'] =  psutil.sensors_battery().percent
		self.data['remaining'] = psutil.sensors_battery().secsleft
		self.data['percent_low'] = round(cfg.LOW, 2)
		self.data['percent_high'] = round(cfg.HIGH, 2)
		self.data['override'] = self.get_override()
		if self.linux:
			self.data['percent_max'] = round(self.get_percent()['percent_max'], 2)
			self.data['name'] = self.get_info()['name']
			self.data['present'] = self.get_info()['present']
		else:
			self.data['percent_max'] = round(100.0, 2)
			self.data['name'] = 'Batterij'
			self.data['present'] = True
		 
		with open(os.path.join(cfg.TMP_DIR, cfg.PLOT_FILE), 'a') as f:
			f.write('%f\t%f\n' % (dt.datetime.now().timestamp(), self.data['percent']))

		with open(os.path.join(cfg.TMP_DIR, cfg.DATA_FILE), 'w') as f:
			for key in self.data.keys():
				f.write(key + '\t' + str(self.data[key]) + '\n')

		return self.data

	def set_charge(self):
		self.data = self.get_data()

		if self.data['override'] == None:
			if self.data['percent'] < cfg.LOW:
				self.start_charge()
			elif self.data['percent'] > cfg.HIGH:
				self.stop_charge()

			elif self.charge == True:
				self.start_charge()
			elif self.charge == False:
				self.stop_charge()

		elif self.data['override'] == True:
			self.start_charge(override=True)
		elif self.data['override'] == False:
			self.stop_charge(override=True)

		self.data = self.get_data()

	def get_override(self):
		try:
			with open(os.path.join(cfg.TMP_DIR, cfg.OVERRIDE_FILE), 'r') as f:
				return literal_eval(f.read())
		except (FileNotFoundError, ValueError):
			with open(os.path.join(cfg.TMP_DIR, cfg.OVERRIDE_FILE), 'w') as f:
				f.write(str(None))
			return None

	def get_status(self):
		with open(os.path.join(cfg.DATA_PATH, 'status')) as file:
			data = file.read()

		if data == 'Discharging\n':
			return False
		elif data == 'Charging\n' or data == 'Full\n':
			return True
		else:
			return None

	def get_percent(self):
		with open(os.path.join(cfg.DATA_PATH, cfg.PERCENT_MAX_FILE)) as file:
			max = file.read()

		with open(os.path.join(cfg.DATA_PATH, cfg.PERCENT_MAX_DESING_FILE)) as file:
			max_design = file.read()

		with open(os.path.join(cfg.DATA_PATH, cfg.PERCENT_NOW_FILE)) as file:
			now = file.read()

		percent = (int(now)/int(max))*100
		percent_max = (int(max)/int(max_design))*100

		return {'percent': round(percent, 2), 'percent_max': percent_max}

	def get_info(self):
		with open(os.path.join(cfg.DATA_PATH, cfg.MANUFACTURER_FILE)) as file:
			manufacturer = file.read()

		with open(os.path.join(cfg.DATA_PATH, cfg.MODEL_FILE)) as file:
			model = file.read()

		with open(os.path.join(cfg.DATA_PATH, cfg.PRESENT_FILE)) as file:
			if file.read() == '1\n':
				present = True
			else:
				present = False

		with open(os.path.join(cfg.DATA_PATH, cfg.TECHNOLOGY_FILE)) as file:
			technology = file.read()

		with open(os.path.join(cfg.DATA_PATH, cfg.TYPE_FILE)) as file:
			type = file.read()

		name = technology + type + ':\n' + manufacturer + model
		name = ' '.join(name.split('\n'))

		return {'name': name, 'present': present}

	def stop_charge(self, override=False):
		if not override:
			self.charge = False
			cfg.charge = False

		self.connection.send(2, 0)
		self.connection.send(3, 0)
		self.connection.send(4, 1)

	def start_charge(self, override=False):
		if not override:
			self.charge = True
			cfg.charge = True

		self.connection.send(2, 1)
		self.connection.send(3, 1)
		self.connection.send(4, 0)

def run():
	try:
		if sys.platform == 'linux':
			Battery()
		else:
			Battery(linux=False)
	except Exception as e:
		log.error(str(e))
		#with open(os.path.join(TMP_DIR, LOG_FILE), 'a') as o:
		#	o.write(str(dt.datetime.now()) + '\tError: ' + str(e) + '\n')


if __name__ == '__main__':
	# if not DEBUG:
	# 	log.info('updating system')
	# 	os.system('~/.adapter/update.sh')

	log.info('Starting data')
	while True:
		run()
		time.sleep(INTERVAL)
