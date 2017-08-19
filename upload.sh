#!/usr/bin/env bash

path=~/.adapter

pwd=$PWD
cd ~/.adapter/

sed -i "s|$HOME|HOME|g" $path/gui.desktop
if/ [ $DESKTOP_SESSION != "gnome" ]
    then
    sed -i "s|battery-symbolic.symbolic|gnome-power-manager|g" $path/gui.desktop
fi

git add .
git commit -m "$@"
git push

sed -i "s|HOME|$HOME|g" $path/gui.desktop
if/ [ $DESKTOP_SESSION != "gnome" ]
    then
    sed -i "s|gnome-power-manager|battery-symbolic.symbolic|g" $path/gui.desktop
fi


cd $pwd
