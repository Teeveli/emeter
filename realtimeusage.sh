#!/bin/bash

#User definable variables
serveraddress="192.168.0.100"
dbname="emeter"
table="realtimeuse"
column="Watts"

query="UPDATE ${table} SET ${column} = $1 WHERE ID = 0"
mysql -h"${serveraddress}" -D"${dbname}" -e"${query}"
