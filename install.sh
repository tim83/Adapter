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
	sudo pip3 install shutil
	
elif [ "$os" == "opensuse" ]
	then
	sudo zypper install python3 python3-pip python3-wheel python3-pyqt5
	sudo pip3 install os
	sudo pip3 install sys
	sudo pip3 install datetime
	sudo pip3 install Pillow
	sudo pip3 install matplotlib
	sudo pip3 install PySerial
	sudo pip3 install shutil
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

sed -i "s/vnctim/$USER/g" $path/gui.desktop
sed -i "s/vnctim/$USER/g" $path/data.desktop
chmod +x $path/data.desktop $path/gui.desktop

sudo sh -c "echo "@reboot $HOME/.adapter/data.py" /var/spool/cron/$USER"
ln -sf $path/gui.desktop $(xdg-user-dir DESKTOP)/battery-monitor.desktop
ln -sf $path/gui.desktop /usr/share/applications/
sudo ln -sf $path/gui.py /usr/local/bin/battery-monitor
