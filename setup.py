#! /usr/bin/python3

from distutils.core import setup
from os.path import expanduser

setup(
	name='adapterctl',
	version='0.45.5',
	packages=['adapterctl'],
	url='https://github.com/tim83/adapterctl',
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
		'PySerial', 'bokeh'
	],
	scripts=['bin/adapterctl'],
	data_files = [
		('share/applications', ['data/org.adapterctl.gui.desktop']),
		(expanduser('~/.config/autostart'), ['data/org.adapterctl.background.desktop']),
	],
	include_package_data = True,
    package_data = {
        '': ['*.ini'],
        '': ['default.ini'],
	    '': ['startbokeh.sh']
    },
)

# upload: ./setup.py sdist upload
