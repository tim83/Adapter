#! /usr/bin/python3

from configparser import ConfigParser
from os.path import join, dirname, expanduser
from ast import literal_eval
import argparse

PROJECT_DIR = dirname(__file__)

config = ConfigParser()
config.read([
	join(PROJECT_DIR, 'default.ini'),
	join(PROJECT_DIR, 'custom.ini'),
	expanduser('~/.config/adapter.ini')
])

for section in config.sections():
	for option in config.options(section):
		str_value = config.get(section, option)
		try:
			value = literal_eval(str_value)
		except (ValueError, SyntaxError):
			value = str_value
		#print('{section} - {option}: {value} ({type})'.format(section=section, option=option, value=value, type=type(value)))
		name = option.upper()
		if type(value) == str:
			exec('{var} = \'{value}\''.format(var=name, value=value))
		else:
			exec('{var} = {value}'.format(var=name, value=value))
		exec('print(\'{name} = {value}\')'.format(name=name, value=value))

def get_logger(name):
	import logging, os
	logFormatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s] %(message)s')
	log = logging.getLogger(name)

	fileHandler = logging.FileHandler(os.path.join(TMP_DIR, LOG_FILE))
	fileHandler.setFormatter(logFormatter)
	log.addHandler(fileHandler)

	consoleHandler = logging.StreamHandler()
	consoleHandler.setFormatter(logFormatter)
	log.addHandler(consoleHandler)

	if DEBUG:
		log.level = logging.DEBUG
	elif VERBOSE:
		log.level = logging.INFO

	return log

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('actie', help='Welke module gestart moet worden (background, gui)')
	parser.add_argument('-v', '--verbose', help='Geef feedback', action='store_true')
	parser.add_argument('-q', '--quiet', help='Geef geen output', action='store_true')
	parser.add_argument('-d', '--debug', help='Activeer debug mode', action='store_true')
	args = parser.parse_args()

	if args.verbose:
		VERBOSE = True

	if args.quiet:
		VERBOSE = False

	if args.debug:
		DEBUG = True

	exec_gui = False
	exec_data = False
	exec_usb = False

	if args.actie.lower() in ['background', 'data']:
		exec_data = True
		import adapterctl.data
	elif args.actie.lower() == 'gui':
		exec_gui = True
		import adapterctl.gui
	elif args.actie.lower() == 'usb':
		exec_usb = True
		import adapterctl.usb
	else:
		parser.print_help()
else:
	exec_gui = False
	exec_data = False
	exec_usb = False