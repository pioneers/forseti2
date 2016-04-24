cd
rm scan_wifi.sh*
wget https://raw.githubusercontent.com/pioneers/forseti2/2016/scan_wifi.sh
sudo chmod 777 scan_wifi.sh
rm dawn-darwin-x64.tar.gz*
wget https://dl.dropboxusercontent.com/s/5f0idms5spxxr11/dawn-darwin-x64.tar.gz
sudo tar -xvzf dawn-darwin-x64.tar.gz
rm dawn-darwin-x64.tar.gz*
sudo rm -rf /opt/driver_station
sudo mv dawn-darwin-x64 /opt/driver_station
sudo chmod -R 777 /opt/driver_station
DEFAULT_FIELD_IP=192.168.0.101
echo -n "Field IP (default $DEFAULT_FIELD_IP) ?"
read FIELD_IP
[ -z $FIELD_IP ] && FIELD_IP="$DEFAULT_FIELD_IP"
echo -n "$FIELD_IP" > /opt/driver_station/lcm_bridge_addr.txt
echo -n "Station number ?"
read STATION_NUMBER
echo -n "$STATION_NUMBER" > /opt/driver_station/station_number.txt
