#! /usr/bin/python3

import datetime as dt
from serial.serialutil import SerialException
from ast import literal_eval
import os, time, psutil, sys, logging, signal

# if __name__ == '__main__':
from adapterctl.__init__ import *
# else:
# 	from __main__ import *
from adapterctl.usb import Connection

log = get_logger('data')

files = os.listdir(DATA_PATH)
for file in files:
	if "BAT" in file:
		DATA_PATH = os.path.join(DATA_PATH, file)

class Battery():
	def __init__(self, connection, single=False, linux=True):
		self.linux = linux
		self.connection = connection
		
		os.makedirs(TMP_DIR, exist_ok=True)
		with open(os.path.join(TMP_DIR, PID_FILE), 'w') as f:
			f.write(str(os.getpid()))
			
		signal.signal(signal.SIGALRM, self.set_charge)

		self.charge = IDLE

		while True:
			self.set_charge()
			if single or self.connection == None:
				break
			time.sleep(INTERVAL)

	def get_data(self):
		self.data = {}
		
		try:
			self.data['charging'] = psutil.sensors_battery().power_plugged
			self.data['percent'] =  psutil.sensors_battery().percent
			self.data['remaining'] = psutil.sensors_battery().secsleft
		except AttributeError:
			self.data['charging'] = self.get_status()
			self.data['percent'] =  self.get_percent()['percent']
			self.data['remaining'] = self.get_secs_left()
		self.data['percent_low'] = round(LOW, 2)
		self.data['percent_high'] = round(HIGH, 2)
		self.data['override'] = self.get_override()
		if self.linux:
			self.data['percent_max'] = round(self.get_percent()['percent_max'], 2)
			self.data['name'] = self.get_info()['name']
			self.data['present'] = self.get_info()['present']
		else:
			self.data['percent_max'] = round(100.0, 2)
			self.data['name'] = 'Batterij'
			self.data['present'] = True
		 
		with open(os.path.join(TMP_DIR, PLOT_FILE), 'a') as f:
			f.write('%f\t%f\n' % (dt.datetime.now().timestamp(), self.data['percent']))

		with open(os.path.join(TMP_DIR, DATA_FILE), 'w') as f:
			for key in self.data.keys():
				f.write(key + '\t' + str(self.data[key]) + '\n')

		return self.data

	def set_charge(self, *args):
		self.data = self.get_data()

		if self.data['override'] == None:
			if self.data['percent'] < LOW:
				self.start_charge()
			elif self.data['percent'] > HIGH:
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
			with open(os.path.join(TMP_DIR, OVERRIDE_FILE), 'r') as f:
				return literal_eval(f.read())
		except (FileNotFoundError, ValueError):
			with open(os.path.join(TMP_DIR, OVERRIDE_FILE), 'w') as f:
				f.write(str(None))
			return None

	def get_status(self):
		with open(os.path.join(DATA_PATH, 'status')) as file:
			data = file.read()

		if data == 'Discharging\n':
			return False
		elif data == 'Charging\n' or data == 'Full\n':
			return True
		else:
			return None

	def get_percent(self):
		with open(os.path.join(DATA_PATH, PERCENT_MAX_FILE)) as file:
			max = file.read()

		with open(os.path.join(DATA_PATH, PERCENT_MAX_DESING_FILE)) as file:
			max_design = file.read()

		with open(os.path.join(DATA_PATH, PERCENT_NOW_FILE)) as file:
			now = file.read()

		percent = (int(now)/int(max))*100
		percent_max = (int(max)/int(max_design))*100

		return {'percent': percent, 'percent_max': percent_max}

	def get_secs_left(self):
		import subprocess
		result = subprocess.Popen('acpi -b | cut -d \' \' -f5', stdout=subprocess.PIPE, shell=True)
		read = result.stdout.read().decode('utf-8')[:-1]
		time = dt.datetime.strptime(read, '%H:%M:%S').time()
		diff = dt.timedelta(hours=time.hour, minutes=time.minute, seconds=time.second)
		secs = diff.total_seconds()
		return secs

	def get_info(self):
		with open(os.path.join(DATA_PATH, MANUFACTURER_FILE)) as file:
			manufacturer = file.read()

		with open(os.path.join(DATA_PATH, MODEL_FILE)) as file:
			model = file.read()

		with open(os.path.join(DATA_PATH, PRESENT_FILE)) as file:
			if file.read() == '1\n':
				present = True
			else:
				present = False

		with open(os.path.join(DATA_PATH, TECHNOLOGY_FILE)) as file:
			technology = file.read()

		with open(os.path.join(DATA_PATH, TYPE_FILE)) as file:
			type = file.read()

		name = technology + type + ':\n' + manufacturer + model
		name = ' '.join(name.split('\n'))

		return {'name': name, 'present': present}

	def stop_charge(self, override=False):
		if not override:
			self.charge = False
		if self.connection:
			self.connection.send(2, 0)
			self.connection.send(3, 0)
			self.connection.send(4, 1)

	def start_charge(self, override=False):
		if not override:
			self.charge = True
		if self.connection:
			self.connection.send(2, 1)
			self.connection.send(3, 1)
			self.connection.send(4, 0)

def run(single=False):
	try:
		try:
			connection = Connection()
		except:
			connection = None
			log.warning('No controler connected')
		Battery(connection, single=single)
	except Exception as e:
		log.error(str(e))


if __name__ == '__main__':
	log.info('Starting data')
	while True:
		run(single=True)
		time.sleep(INTERVAL)
