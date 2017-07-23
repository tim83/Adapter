#! /usr/bin/python3

from usb import *
from settings import *

import datetime as dt
import os

files = os.listdir(DATA_PATH)
for file in files:
	if "BAT" in file:
		DATA_PATH += file + '/'

connection = Connection()

class Battery():
	def __init__(self, passive=False):
		self.passive = passive
		while True:
			self.data = self.get_data()
			os.sleep(INTERVAL)

	def get_data(self):
		self.data = {}

		self.data['charging'] = self.get_status()
		self.data['percent'] = round(self.get_percent()['percent'], 2)
		self.data['percent_low'] = round(LOW_LEVEL, 2)
		self.data['percent_high'] = round(HIGH_LEVEL, 2)
		self.data['percent_max'] = round(self.get_percent()['percent_max'], 2)
		self.data['name'] = self.get_info()['name']
		self.data['present'] = self.get_info()['present']

		with open(PLOT_FILE, 'a') as f:
			f.write('%f\t%f' % (dt.datetime.now().timestamp(), self.data['percent']))

		with open(DATA_FILE, 'a') as f:
			for key in self.data.keys():
				f.write(key + '\t' + str(self.data[key]))


		if not self.passive:
			if self.data['percent'] > HIGH_LEVEL:
				self.stop_charge()
			if self.data['percent'] < LOW_LEVEL:
				self.start_charge()

		return self.data

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

	def stop_charge(self):
		connection.send('0')

	def start_charge(self):
		connection.send('1')

if __name__ == '__main__':
	Battery()