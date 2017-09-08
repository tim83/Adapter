#! /usr/bin/python3

from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import matplotlib.dates as mdates
import matplotlib.collections as col

import datetime as dt
from ast import literal_eval
import os, socket, psutil, logging

#from settings import *
if __name__ == '__main__':
	from adapterctl.__init__ import *
else:
	from __main__ import *
from adapterctl.data import run as run_data

# logging.basicConfig(format='[%(asctime)s - %(name)s - %(levelname)s] %(message)s', filename=os.path.join(TMP_DIR, LOG_FILE))
# log = logging.getLogger('GUI')
# if DEBUG:
# 	log.level = logging.DEBUG
# elif VERBOSE:
# 	log.level = logging.INFO
log = cfg.get_logger('GUI')

def style(item, fontsize=12, fontfamily="Noto Sans", fontcolor='black'):
	item.setStyleSheet('font-size: ' + str(fontsize) + 'pt; font-family: ' + str(fontfamily) + ', sans-serif ; color: ' + str(fontcolor) + ';')

def is_connected():
	try:
		# connect to the host -- tells us if the host is actually
		# reachable
		socket.create_connection(("www.github.com", 80))
		return True
	except OSError:
		return False

class Gui(QMainWindow):
	def __init__(self):
		log.info('Starting GUI')
		super().__init__()
		self.font = 12

		self.menu = self.menuBar()

		self.file_menu = self.menu.addMenu('Bestand')
		self.manual_menu = self.file_menu.addMenu('Lader')

		self.auto_item = QAction('Automatisch', self)
		self.auto_item.setShortcut('Ctrl+a')
		self.manual_menu.addAction(self.auto_item)

		self.on_item = QAction('Aan', self)
		self.on_item.setShortcut('Ctrl+1')
		self.manual_menu.addAction(self.on_item)

		self.off_item = QAction('Uit', self)
		self.off_item.setShortcut('Ctrl+0')
		self.manual_menu.addAction(self.off_item)

		self.quit_item = self.file_menu.addAction('Afsluiten')

		self.view_menu = self.menu.addMenu('Beeld')
		self.large_item = QAction('Lettergrootte vergroten', self)
		self.large_item.setShortcut('Ctrl++')
		self.view_menu.addAction(self.large_item)

		self.small_item = QAction('Lettergrootte verkleinen', self)
		self.small_item.setShortcut('Ctrl+-')
		self.view_menu.addAction(self.small_item)

		# self.tools_menu = self.menu.addMenu('Hulpmiddelen')
		# self.update_item = QAction('Update', self)
		# self.update_item.setShortcut('Ctrl+U')
		# self.tools_menu.addAction(self.update_item)

		self.menu.triggered.connect(self.selected)

		self.widget = Widget(self)
		self.setCentralWidget(self.widget)
		self.setWindowTitle(self.widget.data['name'])
		if os.environ.get('DESKTOP_SESSION') == 'gnome':
			QIcon.setThemeName('Arc-Maia')
			self.setWindowIcon(QIcon.fromTheme('gnome-power-manager'))
		else:
			self.setWindowIcon(QIcon.fromTheme('battery-symbolic.symbolic'))
		style(self, fontsize=self.font)
		self.show()

	def selected(self, data):
		signal = data.text().replace('&','')

		if signal == 'Afsluiten':
			log.critical('Exiting')
			self.stop()
		elif signal == 'Lettergrootte vergroten':
			self.font += 1
			log.debug('Fontsize to %d' % self.font)
			style(self, fontsize=self.font)
		elif signal == 'Lettergrootte verkleinen':
			self.font -= 1
			log.debug('Fontsize to %d' % self.font)
			style(self, fontsize=self.font)
		elif 'Aan' in signal:
			log.debug('Settings override to on')
			with open(os.path.join(cfg.TMP_DIR, cfg.OVERRIDE_FILE), 'w') as f:
				f.write(str(True))
			Set_charge().start()
			self.widget.update()
		elif 'Uit' in signal:
			log.debug('Settings override to off')
			with open(os.path.join(cfg.TMP_DIR, cfg.OVERRIDE_FILE), 'w') as f:
				f.write(str(False))
			Set_charge().start()
			self.widget.update()
		elif 'Automatisch' in signal:
			log.debug('Settings override to auto')
			with open(os.path.join(cfg.TMP_DIR, cfg.OVERRIDE_FILE), 'w') as f:
				f.write(str(None))
			Set_charge().start()
			self.widget.update()
		elif signal == 'Update':
			if is_connected():
				log.debug('Starting update')
				self.update_thread = Update()
				self.update_thread.start()
			else:
				log.warning('Geen internetconnectie')
				self.widget.error('Geen internet connectie', fatal = False)

	def stop(self):
		self.widget.stop()



class Widget(QWidget):
	def __init__(self, mainwindow):
		super().__init__()
		self.mainwindow = mainwindow
		self.stoped = False
		self.interval = 3000 # INTERVAL * 1000

		self.start_ui()

		self.timer = QTimer(self)
		self.timer.timeout.connect(self.update)
		self.timer.start(self.interval)

	def get_data(self):
		self.data = {}
		try:
			with open(os.path.join(cfg.TMP_DIR, cfg.DATA_FILE), 'r') as f:
				lines = f.read().split('\n')
				for l in lines:
					if l != '':
						d = l.split('\t')
						try:
							self.data[d[0]] = literal_eval(d[1])
						except:
							self.data[d[0]] = d[1]
		except FileNotFoundError:
			self.error('Het achtergrond proces is niet niet actief.', fatal=True)

		self.data['percent'] = psutil.sensors_battery().percent
		self.data['charging'] = psutil.sensors_battery().power_plugged
		self.data['remaining'] = psutil.sensors_battery().secsleft

		return self.data

	def start_ui(self):
		self.data = self.get_data()

		if not self.data['present']:
			self.error('Geen batterij gevonden.')

		self.layout = QGridLayout()

		self.override_warning = QLabel('')
		self.layout.addWidget(self.override_warning, 0, 1, 1, 2)
		self.layout.addWidget(QLabel('Opladen:'), 1, 1)
		self.layout.addWidget(QLabel('Percentage:'), 2, 1)
		self.layout.addWidget(QLabel('Tijd te gaan:'), 3, 1)
		#self.layout.addWidget(QLabel('Minimum:'), 3, 1)
		#self.layout.addWidget(QLabel('Maximum:'), 4, 1)
		#self.layout.addWidget(QLabel('Maximum oplaadcapaciteit:'), 5, 1)

		self.charging = QLabel('')
		self.percent = QLabel('')
		self.time_left = QLabel('')
		#self.percent_low = QLabel('')
		#self.percent_high = QLabel('')
		#self.percent_max = QLabel('')

		self.layout.addWidget(self.charging, 1, 2)
		self.layout.addWidget(self.percent, 2, 2)
		self.layout.addWidget(self.time_left, 3, 2)
		#self.layout.addWidget(self.percent_low, 3, 2)
		#self.layout.addWidget(self.percent_high, 4, 2)
		#self.layout.addWidget(self.percent_max, 5, 2)

		self.plot = Plot()
		self.layout.addWidget(self.plot, 6, 1, 2, 2)

		self.stop_button = QPushButton('Sluiten')
		self.stop_button.clicked.connect(self.stop)
		#self.layout.addWidget(self.stop_button, 8, 1, 1, 2)

		self.setLayout(self.layout)
		self.show()
		self.update()

	def update(self):
		self.get_data()
		if self.data['charging']:
			self.charging.setText('\u2714')
		else:
			self.charging.setText('\u2718')

		if self.data['override'] == None:
			self.override_warning.setText('')
			style(self.override_warning, fontsize=1)
			self.mainwindow.auto_item.setText('\u2714 Automatisch')
			self.mainwindow.on_item.setText('    Aan')
			self.mainwindow.off_item.setText('    Uit')

		else:
			self.override_warning.setText('Attentie, de lader staat op manuele modus.')
			style(self.override_warning, fontcolor='red')
			if self.data['override']:
				self.mainwindow.auto_item.setText('    Automatisch')
				self.mainwindow.on_item.setText('\u2714 Aan')
				self.mainwindow.off_item.setText('    Uit')
			else:
				self.mainwindow.auto_item.setText('    Automatisch')
				self.mainwindow.on_item.setText('    Aan')
				self.mainwindow.off_item.setText('\u2714 Uit')
		self.percent.setText('%.2f%%' % self.data['percent'])

		time = dt.timedelta(0, self.data['remaining'])
		if time > dt.timedelta(0):
			self.time_left.setText(str(time).replace('days', 'dagen').replace('day', 'dag'))
		else:
			self.time_left.setText('\u221E')
		#self.percent_low.setText(str(self.data['percent_low']) + '%')
		#self.percent_high.setText(str(self.data['percent_high']) + '%')
		#self.percent_mself.ax.setText(str(self.data['percent_max']) + '%')
		# self.progressbar.setProperty("value", int(self.data['percent']))
		#self.plot.plot()

	def stop(self):
		self.plot.close()
		qApp.quit()
		exit()

	def error(self, error, fatal=True, detail=True):
		box = QMessageBox()
		box.setIcon(QMessageBox.Critical)
		box.setText("Error: %s" % error)
		if detail == True:
			box.setDetailedText(str(self.data))
		elif type(detail) == str:
			box.setDetailedText(detail)
		box.setWindowTitle("Error")
		box.setStandardButtons(QMessageBox.Close)
		box.show()
		style(box)

		if fatal:
			self.box.buttonClicked.connect(self.stop)

	def message(self, message):
		box = QMessageBox()
		box.setIcon(QMessageBox.Information)
		box.setText(message)
		box.setWindowTitle("Batterij montior")
		box.setStandardButtons(QMessageBox.Close)
		box.show()
		style(box)
		return box

plt.style.use('ggplot')
class Plot(QWidget):
	def __init__(self):
		super().__init__()
		self.interval = cfg.INTERVAL

		self.figure = plt.figure()
		self.figure.set_facecolor("#f5f6f7")
		self.canvas = FigureCanvas(self.figure)

		ani = anim.FuncAnimation(self.figure, self.plot, interval=self.interval)

		layout = QVBoxLayout()
		layout.addWidget(self.canvas)
		self.setLayout(layout)

		self.draw()
		self.show()
		self.plot()

	def get_data(self):
		self.data = []
		self.time = []
		with open(os.path.join(cfg.TMP_DIR, cfg.PLOT_FILE), 'r') as f:
			for l in f.readlines():
				d = l.split('\t')
				t = dt.datetime.fromtimestamp(float(d[0]))
				self.time.append(t)
				self.data.append(float(d[1]))
		return self.time, self.data

	def draw(self, *argv):
		self.time, self.data = self.get_data()

		nowTime = dt.datetime.now()
		endTime = nowTime - dt.timedelta(hours=cfg.PERIOD)
		now = mdates.date2num(nowTime)
		end = mdates.date2num(endTime)

		self.ax = self.figure.add_subplot(111)
		self.ax.clear()

		# plt.gcf().autofmt_xdate()
		locator = mdates.AutoDateLocator(minticks=3)
		# formatter = mdates.AutoDateFormatter(locator)
		formatter = mdates.DateFormatter('%H:%M')
		self.ax.xaxis.set_major_locator(locator)
		self.ax.xaxis.set_major_formatter(formatter)

		self.ax.plot(self.time, self.data, 'C4-', lw=2)
		self.ax.set_ylabel('Batterij niveau (%)')
		# self.ax.set_xlabel('Tijd')
		self.ax.set_ylim(0, 100)
		self.ax.set_xlim(end, now)
		self.ax.fill_between(self.time, self.data, facecolor='C4', alpha=0.5)

		high = col.BrokenBarHCollection([(end, now)], [cfg.HIGH, 100], facecolor='red', alpha=0.4)
		low = col.BrokenBarHCollection([(end, now)], [0, cfg.LOW], facecolor='red', alpha=0.4)
		self.ax.add_collection(high)
		self.ax.add_collection(low)
		self.canvas.draw()
	
	def plot(self, *argv):
		self.time, self.data = self.get_data()

		nowTime = dt.datetime.now()
		endTime = nowTime - dt.timedelta(hours=cfg.PERIOD)
		now = mdates.date2num(nowTime)
		end = mdates.date2num(endTime)

		self.ax = self.figure.add_subplot(111)
		self.ax.clear()

		# plt.gcf().autofmt_xdate()
		locator = mdates.AutoDateLocator(minticks=3)
		# formatter = mdates.AutoDateFormatter(locator)
		formatter = mdates.DateFormatter('%H:%M')
		self.ax.xaxis.set_major_locator(locator)
		self.ax.xaxis.set_major_formatter(formatter)

		self.ax.plot(self.time, self.data, 'C4-', lw=2)
		self.ax.set_ylabel('Batterij niveau (%)')
		# self.ax.set_xlabel('Tijd')
		self.ax.set_ylim(0, 100)
		self.ax.set_xlim(end, now)
		self.ax.fill_between(self.time, self.data, facecolor='C4', alpha=0.5)

		high = col.BrokenBarHCollection([(end, now)], [cfg.HIGH, 100], facecolor='red', alpha=0.4)
		low = col.BrokenBarHCollection([(end, now)], [0, cfg.LOW], facecolor='red', alpha=0.4)
		self.ax.add_collection(high)
		self.ax.add_collection(low)

	def stop(self):
		qApp.quit()
		exit()

class Set_charge(QThread):
	def __init__(self):
		QThread.__init__(self)

	def __del__(self):
		self.wait()

	def run(self):
		run_data(single=True)

class Update(QThread):
	def run(self):
		if is_connected():
			log.debug('Start update script')
			os.system('~/.adapter/update.sh')
			log.debug('Finished update script')
		log.debug('Terminating ...')
		self.quit()
		log.debug('Terminated')

if __name__ == '__main__':
	import sys

	app = QApplication(['Batterij monitor'])
	gui = Gui()
	sys.exit(app.exec())
