#!/bin/bash

#User definable variables
dbuname="emeter"
serveraddress="192.168.0.100"
dbname="emeter"
table="electr_hourly"
column1="Timestamp"
column2="KwhUsed"

query="INSERT INTO ${table} (${column1},${column2}) VALUES ('${1}','${2}')"
mysql -h"${serveraddress}" -D"${dbname}" -e"${query}"
