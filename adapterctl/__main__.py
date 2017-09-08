#! /usr/bin/python3

from adapterctl.__init__ import *
from os.path import join
import argparse, sys

log = get_logger('args')

log.debug('Parsing arguments')
parser = argparse.ArgumentParser()
parser.add_argument('actie', help='Welke module gestart moet worden (background, gui)')
parser.add_argument('-v', '--verbose', help='Geef feedback', action='store_true')
parser.add_argument('-q', '--quiet', help='Geef geen output', action='store_true')
parser.add_argument('-d', '--debug', help='Activeer debug mode', action='store_true')
parser.add_argument('-1', '--once', help='Laat de background 1 keer checken en dan stoppen', action='store_true')
parser.add_argument('-s', '--status', help='Pas het het laadpatroon aan (on, off, auto)')
args = parser.parse_args()

log.debug(args)

if args.verbose or VERBOSE:
	log.info('Mode: verbose')
	VERBOSE = True
elif args.quiet or not VERBOSE:
	log.info('Mode: quiet')
	VERBOSE = False
elif args.debug or DEBUG:
	log.info('Mode: debug')
	DEBUG = True

if args.status.lower() == 'on':
	log.debug('Settings override to on')
	with open(join(TMP_DIR, OVERRIDE_FILE), 'w') as f:
		f.write(str(True))
elif args.status.lower() == 'off':
	log.debug('Settings override to off')
	with open(join(TMP_DIR, OVERRIDE_FILE), 'w') as f:
		f.write(str(False))
elif args.status == 'auto':
	log.debug('Settings override to auto')
	with open(join(TMP_DIR, OVERRIDE_FILE), 'w') as f:
		f.write(str(None))

if args.actie.lower() in ['background', 'data']:
	log.info('Starting background')
	from adapterctl.data import run
	import time
	if args.single:
		run()
	else:
		while True:
			run()
			time.sleep(INTERVAL)

elif args.actie.lower() == 'gui':
	log.info('Starting GUI')
	from adapterctl.gui import QApplication, Gui

	app = QApplication(['Batterij monitor'])
	gui = Gui()
	sys.exit(app.exec())
elif args.actie.lower() == 'usb':
	log.info('Starting USB')
	from adapterctl.usb import Connection

	con = Connection()
	con.send(2, 0)
	con.send(3, 0)
	con.send(4, 1)
else:
	log.info('Printing helptext')
	parser.print_help()