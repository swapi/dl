#!/bin/sh

export SCRIPTDIR=`dirname $0`
nohup $SCRIPTDIR/dl.py $* > /dev/null 2>> $SCRIPTDIR/dl.error.log &
