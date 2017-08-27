#! /usr/bin/python3

from ast import literal_eval
from configparser import ConfigParser
from os.path import join, dirname, expanduser
import argparse, sys, os

PROJECT_DIR = dirname(__file__)

print(PROJECT_DIR)
config = ConfigParser()
config.read([
	join(PROJECT_DIR, 'default.ini'),
	join(PROJECT_DIR, 'custom.ini'),
	expanduser('~/.config/adapter.ini')
])
print(config)

for section in config.sections():
	for option in config.options(section):
		str_value = config.get(section, option)
		try:
			value = literal_eval(str_value)
		except (ValueError, SyntaxError):
			value = str_value
		print('{section} - {option}: {value} ({type})'.format(section=section, option=option, value=value, type=type(value)))
		name = option.upper()
		if type(value) == str:
			exec('{var} = \'{value}\''.format(var=name, value=value))
		else:
			exec('{var} = {value}'.format(var=name, value=value))

os.makedirs(TMP_DIR, exist_ok=True)

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

	if args.actie.lower() in ['background', 'data']:
		from adapterctl.data import run, time
		while True:
			run()
			time.sleep(INTERVAL)

	elif args.actie.lower() == 'gui':
		from adapterctl.gui import QApplication, Gui

		app = QApplication(['Batterij monitor'])
		gui = Gui()
		sys.exit(app.exec())
	elif args.actie.lower() == 'usb':
		from adapterctl.usb import Connection

		con = Connection()
		con.send(2, 0)
		con.send(3, 0)
		con.send(4, 1)
	else:
		parser.print_help()