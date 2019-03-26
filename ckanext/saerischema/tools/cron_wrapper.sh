#!/bin/bash
# Run the program given as parameters inside the CKAN virtual environment
# Log the output to ~/logs/cron.log

venv=/usr/lib/ckan/default/bin/activate
logdir=${HOME}/logs
mkdir -p $logdir
logfile=$logdir/cron.log

touch $logfile
echo "`date` Running $@" > $logfile

# VIRTUAL_ENV=/usr/lib/ckan/default

if [ "$VIRTUAL_ENV" == "" ]; then
	source $venv
fi

"$@" >> $logfile 2>&1
