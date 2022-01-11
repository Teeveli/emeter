import RPi.GPIO as GPIO
import time
import os
import sys
from datetime import datetime
import mysql.connector
import subprocess
from threading import Thread

# User definable variables
# ------------------------

channel = 14	# GPIO channel to use for pulse detection
impkwh = 1000	# Imp/Kwh of the used meter. Means that 1000 pulses of the led is 1 Kwh used.


# GPIO setup and variable declarations
# ------------------------------------

GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)
pulses = 0
timenow = time.time()
pulsetime = time.time()
pulseinterval = time.time()


# Set current time to previous full hour as epoch time. We use this time to calculate when an hour is passed to insert used KWh to database every full hour.
startdatetime_evenhour = datetime.now().strftime("%Y-%m-%d %H:00")
start_epochtime_evenhour = datetime.strptime(startdatetime_evenhour, "%Y-%m-%d %H:%M").timestamp()


# Clear console screen and print starting time
os.system("clear")
print("Program started ",datetime.now())


# Threaded loop to update realtime electricity usage to database every 5 seconds.
# Only keeps one record where the data is read.
def elecrealtime():
	while True: # Infinite loop

		time.sleep(5) # Sleep for 5 seconds

		# Calculate Watts in use from time between pulses
		pulsesinhour = 3600/float(pulseinterval) # Divide one hour (in seconds) with the time between pulses. We get pulses in hour.
		watts = pulsesinhour * (1000 / impkwh) # We divide 1000 with impkwh to get multiplier for electricity used. IE. If electricity meter would be 600 impulses for 1kWh used.
		subprocess.Popen(["/home/pi/emeter/realtimeusage.sh", f"{watts}"]) # Insert watts in hour estimate  into db via external bash script run in its own subprocess. This keeps the current script uninterrupted.

# Start realtime electricity calculation loop in its own thread.
t1 = Thread(target = elecrealtime)
t1.start()


# Main loop where pulses are counted and inserted into database every full hour.
while True:
	ch = GPIO.wait_for_edge(channel, GPIO.RISING) # This GPIO command waits for the signal edge, and keeps the program in sleep until signal is detected.

	# When next full hour is up, write the used electricity to database.
	# We calculate the used electricity from pulse flashes counted in the passed hour. 
	if start_epochtime_evenhour <= timenow-3600:

		timestamp = datetime.utcnow() #Current UTC time to insert in database.

		# Call external dbinsert.py in its own process for db insertion,
		# so pulse counting continues without interruption.
		kwhused=pulses * (1000 / impkwh) / 1000 # Use impKwh multiplier and divide the value with 1000 to get kWh used.
		subprocess.Popen(["/home/pi/emeter/dbinsert.sh", f"{timestamp}", f"{kwhused}"]) # Call dbinsert.sh to store the time and used electricity to database.
		pulses = 0 # Pulsecounter resets back to 0.

		# Sets the start time to current full hour for loop to determine next hour passed.
		startdatetime_evenhour = datetime.now().strftime("%Y-%m-%d %H:00")
		start_epochtime_evenhour = datetime.strptime(startdatetime_evenhour, "%Y-%m-%d %H:%M").timestamp()

	else: # If full hour has not passed, we update the realtime counters pulseinterval with every pulse detected.

		# Write pulsecounter to screen and add to counter.
		sys.stdout.write("Pulse [%s] \r" %pulses)
		sys.stdout.flush()
		pulses += 1

		# Get current epoch time and compare it to time on next cycle (pulse detected) and calculate the timedifference
		# Time between pulses are used to calculate realtime electricity usage
		timenow = time.time() # Time now
		pulseinterval = timenow - pulsetime # Time passed between now and time set at the previous pulse.
		pulsetime = time.time() # Set current time to use as difference on next pulse.
		time.sleep(0.1) # Sleep for 100ms to prevent false triggers in GPIO pins. If the pulse would flash faster than 10 times a second, I would start to wonder where the 36Kw of electricity is going!
