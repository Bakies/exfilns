#!/bin/bash
if ! [$1]; then
	exit 1 
fi 

encoded=base64 -w 255 "$1"
echo $encoded | bas
