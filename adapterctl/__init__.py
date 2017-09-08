#! /usr/bin/python3

from ast import literal_eval
from configparser import ConfigParser
from os.path import join, dirname, expanduser
import os

if not __name__ == '__main__':
	from __main__ import *

class Config():
	def __init__(self):
		pass
	def get_logger(self, name):
		import logging, os
		logFormatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s] %(message)s')
		log = logging.getLogger(name)

		fileHandler = logging.FileHandler(os.path.join(self.TMP_DIR, self.LOG_FILE))
		fileHandler.setFormatter(logFormatter)
		log.addHandler(fileHandler)

		consoleHandler = logging.StreamHandler()
		consoleHandler.setFormatter(logFormatter)
		log.addHandler(consoleHandler)

		if self.DEBUG:
			log.level = logging.DEBUG
		elif self.VERBOSE:
			log.level = logging.INFO

		return log

cfg = Config()

cfg.PROJECT_DIR = dirname(__file__)

config = ConfigParser()
config.read([
	join(cfg.PROJECT_DIR, 'default.ini'),
	join(cfg.PROJECT_DIR, 'custom.ini'),
	expanduser('~/.config/adapter.ini')
])

for section in config.sections():
	for option in config.options(section):
		str_value = config.get(section, option)
		try:
			value = literal_eval(str_value)
		except (ValueError, SyntaxError):
			value = str_value
		# print('{section} - {option}: {value} ({type})'.format(section=section, option=option, value=value, type=type(value)))
		name = option.upper()
		if type(value) == str:
			exec('cfg.{var} = \'{value}\''.format(var=name, value=value))
		else:
			exec('cfg.{var} = {value}'.format(var=name, value=value))
cfg.charge = cfg.IDLE
os.makedirs(cfg.TMP_DIR, exist_ok=True)

# def get_logger(name):
# 	import logging, os
# 	logFormatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s] %(message)s')
# 	log = logging.getLogger(name)
#
# 	fileHandler = logging.FileHandler(os.path.join(TMP_DIR, LOG_FILE))
# 	fileHandler.setFormatter(logFormatter)
# 	log.addHandler(fileHandler)
#
# 	consoleHandler = logging.StreamHandler()
# 	consoleHandler.setFormatter(logFormatter)
# 	log.addHandler(consoleHandler)
#
# 	if DEBUG:
# 		log.level = logging.DEBUG
# 	elif VERBOSE:
# 		log.level = logging.INFO
#
# 	return log
