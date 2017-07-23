#! /bin/bash

PATH=~/.adapter

mkdir -p $PATH
cp -rv . $PATH

os=$(cat /etc/os-release | grep ID | cut -d '=' -f2)
if [ "$os" == "manjaro" ]
	then
	sudo pacman -S python3 python-pip python-wheel python-pyqt5	
	sudo pip3 install os
	sudo pip3 install sys
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

chmod +x $PATH/data.desktop $PATH/gui.desktop
ln -sf $PATH/data.desktop ~/.config/autostart/battery-background.desktop
ln -sf $PATH/gui.desktop $(xdg-user-dir DESKTOP)/battery-monitor.desktop
sudo ln -sf $PATH/gui.desktop /usr/local/bin/battery-monitor.desktop
