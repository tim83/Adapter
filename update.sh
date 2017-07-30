#!/usr/bin/env bash

path=~/.adapter

pwd=$PWD
cd ~/.adapter/

git fetch --all
git reset --hard origin/master
sed -i "s|\$HOME|$HOME|g" $path/gui.desktop
sed -i "s|\$HOME|$HOME|g" $path/data.desktop

cd $pwd
