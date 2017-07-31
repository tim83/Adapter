#! /usr/bin/python3

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import matplotlib.dates as mdates
import matplotlib.collections as col

import datetime as dt
from ast import literal_eval
import os, socket

from settings import *
from data import Battery
from usb import Connection

def style(item, fontsize=12, fontfamily="Noto Sans", fontcolor='black'):
	item.setStyleSheet('font-size: ' + str(fontsize) + 'pt; font-family: ' + str(fontfamily) + ', sans-serif ; color: ' + str(fontcolor) + ';')

def is_connected():
	try:
		# connect to the host -- tells us if the host is actually
		# reachable
		socket.create_connection(("www.github.com", 80))
		return True
	except OSError:
		pass
	return False

class Gui(QMainWindow):
	def __init__(self):
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

		self.tools_menu = self.menu.addMenu('Hulpmiddelen')
		self.update_item = QAction('Update', self)
		self.update_item.setShortcut('Ctrl+U')
		self.tools_menu.addAction(self.update_item)

		self.menu.triggered.connect(self.selected)

		self.widget = Widget(self)
		self.setCentralWidget(self.widget)
		self.setWindowTitle(self.widget.data['name'])
		self.setWindowIcon(QIcon('/usr/share/icons/Arc-Maia/devices/symbolic/battery-symbolic.svg')) # '/usr/share/icons/Adwaita/64x64/devices/battery-symbolic.symbolic.png'))
		style(self, fontsize=self.font)
		self.show()

	def selected(self, data):
		signal = data.text().replace('&','')

		if signal == 'Afsluiten':
			self.stop()
		elif signal == 'Lettergrootte vergroten':
			self.font += 1
			style(self, fontsize=self.font)
		elif signal == 'Lettergrootte verkleinen':
			self.font -= 1
			style(self, fontsize=self.font)
		elif 'Aan' in signal:
			with open(os.path.join(DATA_DIR, OVERRIDE_FILE), 'w') as f:
				f.write(str(True))
			Battery(single=True)
			self.widget.update()
		elif 'Uit' in signal:
			with open(os.path.join(DATA_DIR, OVERRIDE_FILE), 'w') as f:
				f.write(str(False))
			Battery(single=True)
			self.widget.update()
		elif 'Automatisch' in signal:
			with open(os.path.join(DATA_DIR, OVERRIDE_FILE), 'w') as f:
				f.write(str(None))
			Battery(single=True)
			self.widget.update()
		elif signal == 'Update':
			if is_connected():
				os.system('~/.adapter/update.sh')
				self.widget.message('Het systeem is geupdate.')
			else:
				self.widget.error('Geen internetconnectie', fatal=False, detail='Probeer het programma opnieuw op te starten als het probleem zich blijft voordoen.')

	def stop(self):
		self.widget.stop()



class Widget(QWidget):
	def __init__(self, mainwindow):
		super().__init__()
		self.mainwindow = mainwindow
		self.stoped = False
		self.interval = INTERVAL * 1000

		self.start_ui()
		self.update()

		self.timer = QTimer(self)
		self.timer.timeout.connect(self.update)
		self.timer.start(self.interval)

	def get_data(self):
		self.data = {}
		with open(os.path.join(DATA_DIR, DATA_FILE), 'r') as f:
			lines = f.read().split('\n')
			for l in lines:
				if l != '':
					d = l.split('\t')
					self.data[d[0]] = d[1]
		return self.data

	def start_ui(self):
		self.data = self.get_data()

		if not literal_eval(self.data['present']):
			self.error('Geen batterij gevonden.')

		self.layout = QGridLayout()

		self.override_warning = QLabel('')
		self.layout.addWidget(self.override_warning, 0, 1, 1, 2)
		self.layout.addWidget(QLabel('Opladen:'), 1, 1)
		self.layout.addWidget(QLabel('Percentage:'), 2, 1)
		self.layout.addWidget(QLabel('Minimum:'), 3, 1)
		self.layout.addWidget(QLabel('Maximum:'), 4, 1)
		self.layout.addWidget(QLabel('Maximum oplaadcapaciteit:'), 5, 1)

		self.charging = QLabel('')
		self.percent = QLabel('')
		self.percent_low = QLabel('')
		self.percent_high = QLabel('')
		self.percent_max = QLabel('')

		self.layout.addWidget(self.charging, 1, 2)
		self.layout.addWidget(self.percent, 2, 2)
		self.layout.addWidget(self.percent_low, 3, 2)
		self.layout.addWidget(self.percent_high, 4, 2)
		self.layout.addWidget(self.percent_max, 5, 2)

		self.plot = Plot()
		self.layout.addWidget(self.plot, 6, 1, 2, 2)

		self.stop_button = QPushButton('Sluiten')
		self.stop_button.clicked.connect(self.stop)
		self.layout.addWidget(self.stop_button, 8, 1, 1, 2)

		self.setLayout(self.layout)
		self.show()

	def update(self):
		self.get_data()
		if literal_eval(self.data['charging']):
			self.charging.setText('\u2714')
		else:
			self.charging.setText('\u2718')

		if literal_eval(self.data['override']) == None:
			self.override_warning.setText('')
			style(self.override_warning, fontsize=1)
			self.mainwindow.auto_item.setText('\u2714 Automatisch')
			self.mainwindow.on_item.setText('    Aan')
			self.mainwindow.off_item.setText('    Uit')

		else:
			self.override_warning.setText('Attentie, de lader staat op manuele modus.')
			style(self.override_warning, fontcolor='red')
			if literal_eval(self.data['override']):
				self.mainwindow.auto_item.setText('    Automatisch')
				self.mainwindow.on_item.setText('\u2714 Aan')
				self.mainwindow.off_item.setText('    Uit')
			else:
				self.mainwindow.auto_item.setText('    Automatisch')
				self.mainwindow.on_item.setText('    Aan')
				self.mainwindow.off_item.setText('\u2714 Uit')

		self.percent.setText(str(self.data['percent']) + '%')
		self.percent_low.setText(str(self.data['percent_low']) + '%')
		self.percent_high.setText(str(self.data['percent_high']) + '%')
		self.percent_max.setText(str(self.data['percent_max']) + '%')
		# self.progressbar.setProperty("value", int(self.data['percent']))

	def stop(self):
		self.message('Thank you for charging with TimAir')
		self.plot.close()
		qApp.quit()
		exit()

	def error(self, error, fatal=True, detail=True):
		self.box = QMessageBox()
		self.box.setIcon(QMessageBox.Critical)
		self.box.setText("Error: %s" % error)
		if detail == True:
			self.box.setDetailedText(str(self.data))
		elif type(detail) == str:
			self.box.setDetailedText(detail)
		self.box.setWindowTitle("Error")
		self.box.setStandardButtons(QMessageBox.Close)
		self.box.show()
		style(self.box)

		if fatal:
			self.box.buttonClicked.connect(self.stop)

	def message(self, error):
		self.box = QMessageBox()
		self.box.setIcon(QMessageBox.Information)
		self.box.setText(error)
		self.box.setWindowTitle("Batterij montior")
		self.box.setStandardButtons(QMessageBox.Close)
		self.box.show()
		style(self.box)

plt.style.use('ggplot')
class Plot(QWidget):
	def __init__(self):
		super().__init__()
		self.interval = INTERVAL * 1000

		self.figure = plt.figure()
		self.figure.set_facecolor("#ececec")
		self.canvas = FigureCanvas(self.figure)

		ani = anim.FuncAnimation(self.figure, self.plot, interval=self.interval)

		layout = QVBoxLayout()
		layout.addWidget(self.canvas)
		self.setLayout(layout)

		self.show()
		self.plot(self.interval)

	def get_data(self):
		self.data = []
		self.time = []
		with open(os.path.join(DATA_DIR, PLOT_FILE), 'r') as f:
			for l in f.readlines():
				d = l.split('\t')
				t = dt.datetime.fromtimestamp(float(d[0]))
				self.time.append(t)
				self.data.append(float(d[1]))
		return self.time, self.data

	def plot(self, interval):
		self.time, self.data = self.get_data()

		nowTime = dt.datetime.now()
		endTime = nowTime - dt.timedelta(hours=PERIOD)
		now = mdates.date2num(nowTime)
		end = mdates.date2num(endTime)

		ax = self.figure.add_subplot(111)
		ax.clear()

		# plt.gcf().autofmt_xdate()
		locator = mdates.AutoDateLocator(minticks=3)
		# formatter = mdates.AutoDateFormatter(locator)
		formatter = mdates.DateFormatter('%H:%M')
		ax.xaxis.set_major_locator(locator)
		ax.xaxis.set_major_formatter(formatter)

		ax.plot(self.time, self.data, 'C4-', lw=2)
		ax.set_ylabel('Batterij niveau (%)')
		# ax.set_xlabel('Tijd')
		ax.set_ylim(0, 100)
		ax.set_xlim(end, now)
		ax.fill_between(self.time, self.data, facecolor='C4', alpha=0.5)

		high = col.BrokenBarHCollection([(end, now)], [HIGH_LEVEL, 100], facecolor='red', alpha=0.4)
		low = col.BrokenBarHCollection([(end, now)], [0, LOW_LEVEL], facecolor='red', alpha=0.4)
		ax.add_collection(high)
		ax.add_collection(low)

		self.canvas.draw()

	def stop(self):
		qApp.quit()
		exit()

if __name__ == '__main__':
	import sys

	app = QApplication(['Batterij monitor'])
	gui = Gui()
	sys.exit(app.exec())
