#!/usr/bin/env bash

path=~/.adapter

pwd=$PWD
cd ~/.adapter/

git fetch --all
git reset --hard origin/master
sed -i "s|HOME|$HOME|g" $path/gui.desktop
if [ $DESKTOP_SESSION != "gnome" ]
    then
    sed -i "s|gnome-power-manager|battery-symbolic.symbolic|g" $path/gui.desktop
fi

cd $pwd
