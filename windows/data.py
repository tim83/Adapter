#! /usr/bin/python3

from usb import *
from settings import *

import datetime as dt
from ast import literal_eval
import os, time, psutil, sys, logging

logging.basicConfig(format='[%(asctime)s - %(name)s - %(levelname)s] %(message)s', filename=os.path.join(DATA_DIR, LOG_FILE))
log = logging.getLogger('data')
if DEBUG:
	log.level = logging.DEBUG

try:
	os.makedirs(DATA_DIR)
	log.debug(DATA_DIR + 'created')
except WindowsError:
	log.debug(DATA_DIR + 'exists')

class Battery():
	def __init__(self, single=True):
		log.info('Starting data')
		self.connection = Connection()
		self.charge = IDLE
			
		self.set_charge()

	def get_data(self):
		self.data = {}

		self.data['charging'] = psutil.sensors_battery().power_plugged
		self.data['percent'] =  psutil.sensors_battery().percent
		self.data['remaining'] = psutil.sensors_battery().secsleft
		self.data['percent_low'] = round(LOW_LEVEL, 2)
		self.data['percent_high'] = round(HIGH_LEVEL, 2)
		self.data['override'] = self.get_override()
		self.data['percent_max'] = round(100.0, 2)
		self.data['name'] = 'Batterij'
		self.data['present'] = True
		 
		with open(os.path.join(DATA_DIR, PLOT_FILE), 'a') as f:
			f.write('%f\t%f\n' % (dt.datetime.now().timestamp(), self.data['percent']))

		with open(os.path.join(DATA_DIR, DATA_FILE), 'w') as f:
			for key in self.data.keys():
				f.write(key + '\t' + str(self.data[key]) + '\n')

		return self.data

	def set_charge(self):
		self.data = self.get_data()

		if self.data['override'] == None:
			if self.data['percent'] < LOW_LEVEL:
				self.start_charge()
			elif self.data['percent'] > HIGH_LEVEL:
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
			with open(os.path.join(DATA_DIR, OVERRIDE_FILE), 'r') as f:
				return literal_eval(f.read())
		except (FileNotFoundError, ValueError):
			with open(os.path.join(DATA_DIR, OVERRIDE_FILE), 'w') as f:
				f.write(str(None))
			return None

	def stop_charge(self, override=False):
		if not override:
			self.charge = False
		self.connection.send(2, 0)
		self.connection.send(3, 0)
		self.connection.send(4, 1)

	def start_charge(self, override=False):
		if not override:
			self.charge = True
		self.connection.send(2, 1)
		self.connection.send(3, 1)
		self.connection.send(4, 0)


def run(single=False):
	try:
		Battery(single=single)
	except Exception as e:
		log.error(str(e))


if __name__ == '__main__':
	while True:
		run()
		time.sleep(INTERVAL)
