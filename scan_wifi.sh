#!/bin/bash

while true; do
	if ifconfig | grep wlan0 -B 0 -A 4 | grep "255.255.255.0"; then
		echo "Connected"
	else 
		sudo iwlist wlan0 scan | egrep "(Gold)|(Blue)" || echo "Not found"
	fi
	sleep 2
done
