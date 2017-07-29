#!/usr/bin/env bash

path=~/.adapter

pwd=$PWD
cd ~/.adapter/

git pull
#sed -i "s/\$HOME/$HOME/g" $path/gui.desktop
#sed -i "s/\$HOME/$HOME/g" $path/data.desktop

cd $pwd
