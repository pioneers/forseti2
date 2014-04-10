#!/bin/bash
# 
# lcm_build.sh
#
# This script installs all forseti2 and LCM dependencies on the rasberry pi.
#

echo "!!! ****** UPDATING SYSTEM ****** !!!"
sudo apt-get update && sudo apt-get upgrade -y

echo "!!! ****** INSTALLING DEPENDENCIES ****** !!!"
sudo apt-get install build-essential libglib2.0-dev openjdk-6-jdk python-dev checkinstall screen -y

echo "!!! ****** DOWNLOADING lcm-1.0.0.tar.gz ****** !!!"
wget https://lcm.googlecode.com/files/lcm-1.0.0.tar.gz

echo "!!! ****** EXTRACTING lcm-1.0.0.tar.gz ****** !!!"
tar xzvf lcm-1.0.0.tar.gz

echo "!!! ****** ENTERING lcm-1.0.0 ****** !!!"
cd lcm-1.0.0/
pwd

echo "!!! ****** CONFIGURING LCM ****** !!!"
./configure

echo "!!! ****** MAKEING LCM ****** !!!"
make

echo "!!! ****** MAKING LCM DEBIAN PACKAGE ****** !!!"
sudo checkinstall

echo "!!! ****** LINKING LCM SHARED LIBRARY ****** !!!"
sudo ldconfig
