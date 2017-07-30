#!/usr/bin/env bash

path=~/.adapter

pwd=$PWD
cd ~/.adapter/

sed -i "s|$HOME|HOME|g" $path/gui.desktop

git add .
git commit -m "$@"
git push

sed -i "s|HOME|$HOME|g" $path/gui.desktop


cd $pwd
