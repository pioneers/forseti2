cd
rm scan_wifi.sh*
wget https://raw.githubusercontent.com/pioneers/forseti2/2016/scan_wifi.sh
sudo chmod 777 scan_wifi.sh
rm dawn-linux-x64.tar.gz*
wget https://dl.dropboxusercontent.com/s/g9ohjmtcfc2ooay/dawn-linux-x64.tar.gz
sudo tar -xvzf dawn-linux-x64.tar.gz
rm dawn-linux-x64.tar.gz*
sudo rm -rf /opt/driver_station
sudo mv dawn-linux-x64 /opt/driver_station
sudo chmod -R 777 /opt/driver_station
DEFAULT_FIELD_IP=192.168.0.101
echo -n "Field IP (default $DEFAULT_FIELD_IP) ?"
read FIELD_IP
[ -z $FIELD_IP ] && FIELD_IP="$DEFAULT_FIELD_IP"
echo -n "$FIELD_IP" > /opt/driver_station/lcm_bridge_addr.txt
echo -n "Station number ?"
read STATION_NUMBER
echo -n "$STATION_NUMBER" > /opt/driver_station/station_number.txt
# # get curl
# sudo apt-get install -y curl

# # get git
# sudo apt-get install -y git

# # get node
# curl -sL https://deb.nodesource.com/setup_5.x | sudo -E bash -
# sudo apt-get install -y nodejs

# wget https://bootstrap.pypa.io/get-pip.py
# sudo python get-pip.py
# # get forseti2
# if [ ! -d "forseti2" ]; then
#   git clone https://github.com/karthik-shanmugam/forseti2.git
# fi
# cd forseti2
# git checkout 2016
# cd ..

# # get daemon
# if [ ! -d "daemon" ]; then
#   git clone https://github.com/rjli13/daemon.git
# fi
# cd daemon
# git checkout field-control
# cd ..

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

# # set up daemon
# cd ../daemon/dawn
# sudo npm install -g electron-prebuilt
# sudo npm install
# npm run-script build
# cd
echo "Driver station deployed"
