sudo stop shill
sudo start shill BLACKLISTED_DEVICES=wlan0
sudo sleep 1
sudo pkill wpa_supplicant
sudo pkill dhcpcd
OO="$(echo $1 $2)"
echo $OO
echo "network={" > tmp2.conf
echo "ssid=\"$1\"" >> tmp2.conf
echo "psk=\"$2\"" >> tmp2.conf
echo "}" >> tmp2.conf
sudo wpa_supplicant -B -iwlan0 -c tmp2.conf
#sudo dhcpcd wlan0
#sudo mkdir /run/resolvconf
#sudo mkdir /run/resolvconf/interface
ifconfig wlan0 192.168.13.100 netmask 255.255.255.0
