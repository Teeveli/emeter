import requests
from datetime import datetime
import re
import mysql.connector
import sys
#import pytz #Used for datetime conversion. Enable if uncommenting the UTC-LOCAL conversion in localizetime


# Read configuration file for database credentials, address and such.
# -------------------------------------------------------------------

f = open("/home/pi/emeter/.emeter_config", "r")
data = f.read()
f.close()


dbuname = re.search('username="(.*)"', data).group(1)
dbpassword = re.search('password="(.*)"', data).group(1)
dbname = re.search('database="(.*)"', data).group(1)
serveraddress = re.search('server="(.*)"', data).group(1)
logdir = re.search('logdir="(.*)"', data).group(1)
table = re.search('table="(.*)"', data).group(1)




# Defining functions.
# -------------------


# Function that converts the timestamp given from FMI result (FMI formatted UTC time as string) to local time (string).
# This function is now changed only to parse the extra letters out, since all data is written as UTC to database, but left commented here for future reference.
def localizetime (fmitime):
	
	str_time = fmitime.replace("T", " ").replace("Z","")

	#fmi_to_str = fmitime.replace("T", " ").replace("Z","")
	#str_to_datetime = datetime.strptime(fmi_to_str, "%Y-%m-%d %H:%M:%f")
	#unnaive_time = str_to_datetime.replace(tzinfo=pytz.utc)
	#localized_time = unnaive_time.astimezone(pytz.timezone("Europe/Helsinki"))
	#str_time = datetime.strftime(localized_time, "%Y-%m-%d %H:%M")
	
	
	return str_time

# Function for inserting the retrieved data to database. This uses hardcoded fields in database containing ID + columns as stated in arguments.
# I considered this single row data to be more usable in this project than using one row for each datatype dynamically.
def insert(TIMESTAMP,TA_PT1H_AVG,TA_PT1H_MAX,TA_PT1H_MIN,RH_PT1H_AVG,WS_PT1H_AVG,WS_PT1H_MAX,WS_PT1H_MIN,WD_PT1H_AVG,PRA_PT1H_ACC,PRI_PT1H_MAX,PA_PT1H_AVG):

	dbconnection = mysql.connector.connect(
	host=serveraddress,
	user=dbuname,
	password=dbpassword,
	database=dbname
	)

	dbcursor = dbconnection.cursor()

	sql = f"INSERT INTO {table} (TIMESTAMP,TA_PT1H_AVG,TA_PT1H_MAX,TA_PT1H_MIN,RH_PT1H_AVG,WS_PT1H_AVG,WS_PT1H_MAX,WS_PT1H_MIN,WD_PT1H_AVG,PRA_PT1H_ACC,PRI_PT1H_MAX,PA_PT1H_AVG) VALUES ('{TIMESTAMP}','{TA_PT1H_AVG}','{TA_PT1H_MAX}','{TA_PT1H_MIN}','{RH_PT1H_AVG}','{WS_PT1H_AVG}','{WS_PT1H_MAX}','{WS_PT1H_MIN}','{WD_PT1H_AVG}','{PRA_PT1H_ACC}','{PRI_PT1H_MAX}','{PA_PT1H_AVG}')"

	dbcursor.execute(sql)

	dbconnection.commit()

	dbcursor.close()
	dbconnection.close()




# Main program section.
# ---------------------


# Searchtime is given as a parameter to FMI search. This sets the start time from which onwards it will get the data.
# As this script is ran hourly 30minutes past hour, the search start time is set to latest full hour.
# The search result will then return only the measurements from last hour. As the FMI search returns data with 1 hour intervals,
# the script returns only one value set.

searchtime = datetime.utcnow().strftime("%Y-%m-%dT%H:00:00Z")



# Try and get the data from FMI. In case of exception, write log. 
try:
	url='https://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature&storedquery_id=fmi::observations::weather::hourly::simple&fmisid=100968&starttime=' + searchtime
	r=requests.get(url)
except Exception as e:
	
	f = open(logdir + "emeter.log", "a")
	f.write(datetime.now().strftime("%Y-%m-%d %H:%M.%S") + "\n" + str(e)+"\n\n")
	f.close()
	
	print(str(e))
	exit()


# Declare empty dictionary for data.
FMI_data = {}


# Try and parse the retrieved GML data and insert the latest entry to database. In case of exception, write log.
# Iterates through all wfs members of the GML and picks up data from there. If the result contains multiple sets of data, it will iterate through all and store the last one.
try:
	for i in re.finditer('<wfs:member>',r.text): # Finds the index of each <wfs:member>. Each member contains one set of data.
		time = re.search('<BsWfs:Time>(.*)</BsWfs:Time>', r.text[i.start():]) # Gets timestamp of the current dataset
		timeparsed = localizetime(time.group(1)) # Strips the timestamp of extra letters FMI data uses.
		parameter = re.search('<BsWfs:ParameterName>(.*)</BsWfs:ParameterName>', r.text[i.start():]) # Gets name of the current found parameter in data.
		value = re.search('<BsWfs:ParameterValue>(.*)</BsWfs:ParameterValue>', r.text[i.start():]) # Gets value of the parameter.

		FMI_data['timestamp']=timeparsed # Insert timestamp of the data to FMI_data dictionary.
		FMI_data[parameter.group(1)]=value.group(1) # Insert retrieved parameter and its value to FMI_data dictionary


	# Insert retrieved data to database. The stored parameter names can be found in the bulk data and in the provided datatypes.txt file.
	insert(FMI_data['timestamp'],FMI_data['TA_PT1H_AVG'],FMI_data['TA_PT1H_MAX'],FMI_data['TA_PT1H_MIN'],FMI_data['RH_PT1H_AVG'],FMI_data['WS_PT1H_AVG'],FMI_data['WS_PT1H_MAX'],FMI_data['WS_PT1H_MIN'],FMI_data['WD_PT1H_AVG'],FMI_data['PRA_PT1H_ACC'],FMI_data['PRI_PT1H_MAX'],FMI_data['PA_PT1H_AVG'])

except Exception as e:
	f = open(logdir + "emeter.log", "a")
	f.write(datetime.now().strftime("%Y-%m-%d %H:%M.%S") + "\n" + str(e)+"\n\n")
	f.close()

	print(str(e))
	exit()

