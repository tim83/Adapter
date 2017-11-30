#! /bin/bash

if [ $1 ]
then
    path=$1
else
    path='.'
fi
bokeh serve --show $path/bokeh.py