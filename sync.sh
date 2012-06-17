#!/bin/sh

if test $# -eq 0 ; then
    echo "Usage: sync.sh [buildmaster]"
    exit 1
fi

BUILDMASTER=$1

SOURCES="master.cfg
         builders.py
         slaves.py
         changesources.py
         schedulers.py
         statustargets.py"

cp $SOURCES $BUILDMASTER

CONFIG=config.py

if [ ! -f $BUILDMASTER/$CONFIG ]; then
    cp $CONFIG $BUILDMASTER
    echo "Please edit $BUILDMASTER/$CONFIG."
fi
