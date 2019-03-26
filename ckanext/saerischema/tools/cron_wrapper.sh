#!/bin/bash

logdir=${HOME}/logs
mkdir -p $logdir
logfile=$logdir/cron.log

touch $logfile
echo "`date` Running $@" >> $logfile

# VIRTUAL_ENV=/usr/lib/ckan/default

if [ "$VIRTUAL_ENV" == "" ]; then
	source ${HOME}/setup
fi

"$@" >> $logfile 2>&1
