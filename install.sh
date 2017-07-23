#! /bin/bash

path=~/.adapter

mkdir -p $path
cp -r . $path/

os=$(cat /etc/os-release | grep ID | cut -d '=' -f2)
if [ "$os" == "manjaro" ]
	then
	sudo pacman -S python3 python-pip python-wheel python-pyqt5 --needed
	sudo pip3 install datetime
	sudo pip3 install Pillow
	sudo pip3 install matplotlib
	sudo pip3 install PySerial
	
elif [ "$os" == "opensuse" ]
	then
	sudo zypper install python3 python3-pip python3-wheel python3-pyqt5
	sudo pip3 install os
	sudo pip3 install sys
	sudo pip3 install datetime
	sudo pip3 install Pillow
	sudo pip3 install matplotlib
	sudo pip3 install PySerial
else
	echo 'Distrubutie niet gevonden.'
	echo 'Gelieven de volgende packatten te installeren voor python3:'
	echo ' - datetime'
	echo ' - os'
	echo ' - sys'
	echo ' - PyQt5'
	echo ' - matplotlib'
	echo ' - PySerial'
	exit
fi

chmod +x $path/data.desktop $path/gui.desktop
ln -sf $path/data.desktop ~/.config/autostart/battery-background.desktop
ln -sf $path/gui.desktop $(xdg-user-dir DESKTOP)/battery-monitor.desktop
sudo ln -sf $path/gui.py /usr/local/bin/battery-monitor
