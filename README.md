# Electricity metering scripts

***NOTE! This repository is not meant to be "ready to deploy" but rather an example of how I built it on my system***

## What, why, where?

This tool is built for logging of my houses electricity usage. The system runs on Raspberry PI (1st gen).
It basically reads led pulses of electricity meter via phototransistor and converts it to usage statistics.
It also keeps hourly log of outside temperature from closest weatherstation. In future I will add an local sensor to the PI.
I also read inside temperature sensors and write graphs of the data with Grafana, but its outside of this repository's scope.
The actual database and web services are on more beefier home NAS.

## File explanation.

- elogger.py		This is the main program for handling pulse counting and calling database insertion scripts.
- elogger.sh		Bash script for automatically creating detached screen (Run at system boot)
- dbinsert.sh		Bash script for pushing data to database (in this case hourly usage of electricity)
- realtimeusage.sh	Bash script for updating data on realtime electricity usage to database.
- getweather.py		Python script to fetch latest weather data from Finnish Meteorological Institute. Called from crontab.
- datatypes.txt		File that lists explanations for the weather data that comes from FMI.
- emeter_config.example	Example configuration file for getweather.py Used to keep user credentials away from script.
- emeter.log		Logfile to write errors from getweather.py in case of errors fetching data.


## Challenges faced during this project.

**Reading the actual signal.**

1. The phototransistor was of unknown kind and encapsulated, so I couldn't just look up its specifications (let alone to know if it actually was transistor or resistor).
  - Solved by measuring different things and making the signal suitable with voltage divider connection. 
Codewise there was this sensitivity to false triggers that was caused possibly to sensors possible slow reaction time. Fixed with adding sleep timer of 100ms after each pulse.

**Threading**

1. Inserting the hourly data to database caused an pause of few seconds to the script, what in turn caused the loop to miss pulses.
  - Solved by running the sql insertion in its own subprocess in linux shell.

2. Creating the realtime electricity usage which updates the kWh value to database every 5 seconds.
  - Solved by creating separate thread that updates the realtime usage to database in subprocess and sleeping 5 seconds after that.

**Speed**

1. Inserting data with python was too slow on 1st gen Raspberry PI. Interperenting Python took too long to compile before the actual insertion happened for my taste (especially for the realtime electricity usage).
  - Solved by changing all the sql operations from Python to Bash scripts. Bash script is considerably faster due not needing to use separate interperenter.

**Weather data from FMI**

- Getting weather data from FMI (Finnish Meteorological Institute) is an chapter of its own. I had previous knowledge of getting data of their open data system as well as from Foreca and Yr.no so this project didn't take so much time as it could have.

- I decided to use FMI instead of Foreca or Yr.no due to Foreca being an paid service after 6 months and being local compared to Yr.no. Advantage of Foreca and Yr.no would be that their data is returned in Json.

- The data returned on FMI's services is in GML (Geography Markup Language) and reading it was bit of an pain. There is libraries for reading GML, but I had problems getting data read that was written inside the actual GML tag. It was too much of an hassle to read it realibly so I wrote my own parser for the data I needed.


**Other**

- Solving the meaning and calculation of imp/kWh (the pulse led of the meter used).
- Datetime manipulation from utc to gmt and vice versa, until I settled to using purely UTC time for db insertion. (Grafana explicitly wants utc time and does the conversion itself automatically)


## Room for improvement

- Extend the logging to elogger.py
- Truncating all the sql operations to one Bash script that takes the database, table, fields and field data as arguments.
- Adding local temperature sensor for outside weather. The current code uses some kind of Interrupt to keep the pulse loop at bay (internal to GPIO library). So I need to explore it bit more and look if I can read the temperature on its own Python script or do I implement it to the current one.
- More commenting to the small scripts
- Renaming the files more sensibly.
- Renaming some of the variables.
- Possibly much more?!
