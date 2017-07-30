#! /usr/bin/python3

from usb import *
from settings import *

import datetime as dt
from serial.serialutil import SerialException
from ast import literal_eval
import os, time, shutil

files = os.listdir(DATA_PATH)
for file in files:
	if "BAT" in file:
		DATA_PATH += file + '/'

class Battery():
	def __init__(self, single=False):
		self.connection = Connection()

		os.makedirs(DATA_DIR, exist_ok=True)

		if IDLE == False:
			self.stop_charge()
		elif IDLE == True:
			self.start_charge()
			
		while True:
			self.set_charge()
			if single:
				break
			else:
				time.sleep(INTERVAL)

	def get_data(self):
		self.data = {}

		self.data['charging'] = self.get_status()
		self.data['percent'] = round(self.get_percent()['percent'], 2)
		self.data['percent_low'] = round(LOW_LEVEL, 2)
		self.data['percent_high'] = round(HIGH_LEVEL, 2)
		self.data['percent_max'] = round(self.get_percent()['percent_max'], 2)
		self.data['name'] = self.get_info()['name']
		self.data['present'] = self.get_info()['present']
		self.data['override'] = self.get_override()
		 
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

	def get_status(self):
		with open(DATA_PATH + 'status') as file:
			data = file.read()

		if data == 'Discharging\n':
			return False
		elif data == 'Charging\n' or data == 'Full\n':
			return True
		else:
			return None

	def get_percent(self):
		with open(DATA_PATH + PERCENT_MAX_FILE) as file:
			max = file.read()

		with open(DATA_PATH + PERCENT_MAX_DESING_FILE) as file:
			max_design = file.read()


		with open(DATA_PATH + PERCENT_NOW_FILE) as file:
			now = file.read()

		percent = (int(now)/int(max))*100
		percent_max = (int(max)/int(max_design))*100

		return {'percent': percent, 'percent_max': percent_max}

	def get_info(self):
		with open(DATA_PATH + MANUFACTURER_FILE) as file:
			manufacturer = file.read()

		with open(DATA_PATH + MODEL_FILE) as file:
			model = file.read()

		with open(DATA_PATH + PRESENT_FILE) as file:
			if file.read() == '1\n':
				present = True
			else:
				present = False

		with open(DATA_PATH + TECHNOLOGY_FILE) as file:
			technology = file.read()

		with open(DATA_PATH + TYPE_FILE) as file:
			type = file.read()

		name = technology + type + ':\n' + manufacturer + model
		name = ' '.join(name.split('\n'))

		return {'name': name, 'present': present}

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


if __name__ == '__main__':
	os.system('~/.adapter/update.sh')
	
	while True:
		try:
			Battery()
		except Exception as e:
			with open(os.path.join(DATA_DIR, LOG_FILE), 'a') as o:
				o.write('Error: ' + str(e) + '\n')
