#! /usr/bin/python3

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import matplotlib.dates as mdates
import matplotlib.collections as col

import datetime as dt

from settings import *

def style(item, fontsize=12, fontfamily="Noto Sans"):
	item.setStyleSheet('font-size: ' + str(fontsize) + 'pt; font-family: ' + str(fontfamily) + ', sans-serif ;')

class Gui(QMainWindow):
	def __init__(self):
		super().__init__()
		self.font = 10
		style(self.widget, fontsize=self.font)

		self.widget = Widget()
		self.setCentralWidget(self.widget)
		style(self.widget)
		self.setWindowTitle(self.widget.data['name'])
		self.show()

	def fullscreen(self):
		self.showMaximized()
		self.font = 68
		style(self.widget, fontsize=self.font)


class Widget(QWidget):
	def __init__(self):
		super().__init__()
		self.stoped = False
		self.interval = INTERVAL * 1000

		self.start_ui()
		self.update()

		self.timer = QTimer(self)
		self.timer.timeout.connect(self.update)
		self.timer.start(self.interval)

	def get_data(self):
		self.data = {}
		with open(DATA_FILE, 'r') as f:
			for l in f.readlines():
				d = l.split('\t')
				self.data[d[0]] = d[1]

	def start_ui(self):
		self.get_data()

		if not self.data['present']:
			self.error('Geen batterij gevonden.')

		self.layout = QGridLayout()

		self.layout.addWidget(QLabel('Opladen?:'), 1, 1)
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
		if self.data['charging']:
			self.charging.setText('\u2714')
		else:
			self.charging.setText('\u2718')
		self.percent.setText(str(self.data['percent']) + '%')
		self.percent_low.setText(str(self.data['percent_low']) + '%')
		self.percent_high.setText(str(self.data['percent_high']) + '%')
		self.percent_max.setText(str(self.data['percent_max']) + '%')
		# self.progressbar.setProperty("value", int(self.data['percent']))

	def stop(self):
		print('Thank you for charging with TimAir')
		self.plot.close()
		qApp.quit()

	def error(self, error):
		self.box = QMessageBox()
		self.box.setIcon(QMessageBox.Critical)
		self.box.setText("Error: %s" % error)
		self.box.setDetailedText(str(self.data))
		self.box.setWindowTitle("Error")
		self.box.setStandardButtons(QMessageBox.Close)
		self.box.show()

		self.box.buttonClicked.connect(self.stop)

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
		with open(PLOT_FILE, 'r') as f:
			for l in f.readlines():
				d = l.split('\t')
				t = dt.datetime.fromtimestamp(float(d[0]))
				self.time.append(t)
				self.data.append(float(d[1]))

	def plot(self, interval):
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

if __name__ == '__main__':
	import sys

	app = QApplication(sys.argv)
	gui = Gui()
	sys.exit(app.exec())