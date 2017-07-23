#! /bin/bash

PATH=~/.adapter

mkdir -p $PATH
cp -rv . $PATH

chmod +x $PATH/data.desktop $PATH/gui.desktop
ln -sf $PATH/data.desktop ~/.config/autostart/battery-background.desktop
ln -sf $PATH/gui.desktop $(xdg-user-dir DESKTOP)/battery-monitor.desktop
sudo ln -sf $PATH/gui.desktop /usr/local/bin/battery-monitor.desktop
