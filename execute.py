#! /usr/bin/python3

from gui import *
from data import *
import sys

app = QApplication(sys.argv)
gui = Gui()
sys.exit(app.exec())
