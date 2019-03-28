#!/bin/bash
# Run the program given as parameters inside the CKAN virtual environment
# Log the output to ~/logs/cron.log

# Configuration:
venv=/usr/lib/ckan/default/bin/activate
logdir=${HOME}/logs

# Initialise the log file (create a new one each time to prevent disk filling up)
mkdir -p $logdir
progname=`basename $1`
logfile=$logdir/${progname}.log
touch $logfile
echo "`date` Running $@" > $logfile

# If inside a virtualenv then just run the command
# otherwise source the virtualenv script before running
# Looking for:
# VIRTUAL_ENV=/usr/lib/ckan/default

if [ "$VIRTUAL_ENV" == "" ]; then
	source $venv
fi

"$@" >> $logfile 2>&1
