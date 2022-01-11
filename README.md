## Electricity metering scripts

*** NOTE! This repository is not meant to be "ready to deploy" but rather an example of how I built it on my system ***

# What, why, where?

This pile of scripts is how I built logging of my houses electricity usage. The system runs on Raspberry PI (1st gen).
It basically reads led pulses of electricity meter via phototransistor and converts it to usage statistics.
It also keeps hourly log of outside temperature from closest weatherstation. In future I will add an local sensor to the PI.
I also read inside temperature sensors and write graphs of the data with Grafana, but its outside of this repository's scope.
The actual database and web services are on more beefier home NAS.

# File explanation

elogger.py		This is the main program for handling pulse counting and calling database insertion scripts.
elogger.sh		Bash script for automatically creating detached screen (Run at system boot)
dbinsert.sh		Bash script for pushing data to database (in this case hourly usage of electricity)
realtimeusage.sh	Bash script for updating data on realtime electricity usage to database.
getweather.py		Python script to fetch latest weather data from Finnish Meteorological Institute. Called from crontab.
datatypes.txt		File that lists explanations for the weather data that comes from FMI.
emeter_config.example	Example configuration file for getweather.py Used to keep user credentials away from script.
emeter.log		Logfile to write errors from getweather.py in case of errors fetching data.

