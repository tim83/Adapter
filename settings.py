import os

from settings_common import *

if os.uname()[1] in ENERGY_HOSTNAMES + ['pc-tim']:
	from settings_energy import *
elif os.uname()[1] in CHARGE_HOSTNAMES:
	from settings_charge import *
else:
	raise ValueError('Device not recognised.')