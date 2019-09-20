#! /usr/bin/python3

# if __name__ == '__main__':
# 	from adapterctl.__init__ import *
# else:
# 	from __main__ import *
import datetime as dt
from ast import literal_eval
import os, socket, psutil, logging, signal, subprocess
from time import sleep
from adapterctl.__init__ import *
import random as r
log = get_logger('Bokeh')

from adapterctl.data import run as run_data

def append_data():
	#with open(os.path.join(TMP_DIR, PLOT_FILE), 'a') as f:
	#	f.write('%f\t%f\n' % (dt.datetime.now().timestamp(), r.randint(0,100))) # psutil.sensors_battery().percent))
	
	# run_data(single=True)
	
	try:	
		with open(os.path.join(TMP_DIR, PID_FILE), 'r') as f:
			pid = f.read()
	
		os.kill(int(pid), signal.SIGALRM)
	except:
		subprocess.Popen(['adapterctl', 'data'])
		sleep(1)
	

def get_plot_data():
	data = []
	time = []
	with open(os.path.join(TMP_DIR, PLOT_FILE), 'r') as f:
		for l in f.readlines():
			d = l.split('\t')
			t = dt.datetime.fromtimestamp(float(d[0]))
			time.append(t)
			data.append(float(d[1]))
	return time, data

def get_data():
	data = {}
	try:
		with open(os.path.join(TMP_DIR, DATA_FILE), 'r') as f:
			lines = f.read().split('\n')
			for l in lines:
				if l != '':
					d = l.split('\t')
					try:
						data[d[0]] = literal_eval(d[1])
					except:
						data[d[0]] = d[1]
	except FileNotFoundError:
		pass
	
	#data = {'charging': True, 'percent': r.randint(0,100), 'remaining': '5h', 'override': True}
	return data


from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox, column
from bokeh.models import ColumnDataSource, TableColumn, DataTable, BoxAnnotation
from bokeh.models.widgets import Slider, TextInput, Select, PreText
from bokeh.plotting import figure

append_data()
time, data  = get_plot_data()
source = ColumnDataSource(data=dict(time=time, data=data))

plot = figure(plot_height=400, plot_width=800, title="Batterijgeschiedenis", x_range=[dt.datetime.now() - dt.timedelta(0,PERIOD),dt.datetime.now()], y_range=[0,100], tools=['box_zoom','pan','reset'])
plot.line('time', 'data', source=source, line_width=3, line_alpha=0.6)

top_box = BoxAnnotation(bottom=HIGH, fill_color='red', fill_alpha=0.1)
bottom_box = BoxAnnotation(top=LOW, fill_color='red', fill_alpha=0.1)
plot.add_layout(top_box)
plot.add_layout(bottom_box)

def update_plot():
	time, data  = get_plot_data()
	source.data = dict(time=time, data=data)
	plot.x_range.start = dt.datetime.now() - dt.timedelta(hours=PERIOD)
	plot.x_range.end = dt.datetime.now()
	
def update_data():
	data = get_data()
	if data['charging']:
		charging = '\u2714'
	else:
		charging = '\u2718'
	if type(data['remaining']) == str:
		time = str(dt.timedelta(seconds=0))
	else:
		time = str(dt.timedelta(seconds=data['remaining']))
	time_nl = time.replace('days', 'dagen').replace('day', 'dag')
	stats.text = 'Opladen:\t{charge}\nPercentage:\t{percent}%\nTijd resterend:\t{time}'.format(charge=charging, percent=round(data['percent'], 2), time=time_nl)
	o = data['override']
	if o == True:
		mode.value = 'Opladen'
	elif o == False:
		mode.value = 'Ontladen'
	elif o == None:
		mode.value = 'Automatisch'
	
def update(*args, **kwargs):
	append_data()
	update_data()
	update_plot()

def set_charge(attrname, old, new):
	if new == 'Automatisch':
		with open(os.path.join(TMP_DIR, OVERRIDE_FILE), 'w') as f:
			f.write(str(None))
	elif new == 'Opladen':
		with open(os.path.join(TMP_DIR, OVERRIDE_FILE), 'w') as f:
			f.write(str(True))
	elif new == 'Ontladen':
		with open(os.path.join(TMP_DIR, OVERRIDE_FILE), 'w') as f:
			f.write(str(False))
	append_data()
	update()

stats = PreText(text='', width=500)
mode = Select(value='Automatisch', options=['Automatisch', 'Opladen', 'Ontladen'], title='Modus')
mode.on_change('value', set_charge)
update()

text = widgetbox(mode, stats)
curdoc().add_root(row(text, plot, width=1300))
curdoc(). add_periodic_callback(update, 1000*INTERVAL)
curdoc().title = "Batterijmonitor"
