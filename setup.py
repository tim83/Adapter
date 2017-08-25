#! /usr/bin/python3

from distutils.core import setup
from os.path import expanduser

setup(
	name='adapter',
	version='0.1',
	packages=['adapterctl'],
	url='https://github.com/tim83/adapter',
	license='GNU General Public License',
	author='Tim Mees',
	author_email='tim.mees83g@gmail.com',
	description=' Een programma om op linux een arduino aan te sturren om zo dmv selectief laden de batterijduur te verlengen ',
	install_requires=[
		'datetime',
		'configparser',
		'argparse',
		'psutil',
		'PyQt5',
		'matplotlib',
		'PySerial'
	],
	scripts=['bin/adapterctl'],
	data_files = [
		('share/applications', ['data/org.adapterctl.gui.desktop']),
		(expanduser('~/.config/autostart'), ['data/org.adapterctl.background.desktop']),
	],
)