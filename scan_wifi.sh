#!/bin/bash

while true; do
	if ifconfig | grep wlan0 -B 0 -A 4 | grep "Mask"; then
		echo "Connected"
	else 
		sudo iwlist wlan0 scan | egrep "(Gold)|(Blue)" || echo "Not found"
	fi
	sleep 2
done
