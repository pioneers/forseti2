#!/usr/bin/env bash

cd

echo "Field Control Dawn URL:";
read url;
if [ -n "$url" ]; then
    wget $url
    tar -xvzf dawn-linux-x64.tar.gz
    rm dawn-linux-x64.tar.gz*
fi

echo "Type Bridge Address:";
read address;
if [ -z "$address" ]; then
    address="192.168.128.138";
fi
echo -n $address > ~/Desktop/bridge_address.txt;

echo "Bridge Station (0-1 For Blue, 2-3 For Gold):"
read station;
if [ -z "$station" ]; then
    station=0;
fi
echo -n $station > ~/Desktop/station_number.txt;

# # get lcm
# sudo apt-get install -y build-essential
# sudo apt-get install -y libglib2.0-dev
# sudo apt-get install -y python-dev

# if [ ! -d "lcm-1.3.1" ]; then
#   wget https://github.com/lcm-proj/lcm/releases/download/v1.3.1/lcm-1.3.1.zip
#   unzip lcm-1.3.1
#   cd lcm-1.3.1
#   ./configure
#   make
#   sudo make install
#   sudo ldconfig
# fi

# # set up forseti2
# cd ../forseti2
# ./gen-types.sh
# sudo pip install tornado

echo "Driver station deployed"
