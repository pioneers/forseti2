# get curl
sudo apt-get install -y curl

# get git
sudo apt-get install -y git

# get node
curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -
sudo apt-get install -y nodejs

# get forseti2
git clone https://github.com/karthik-shanmugam/forseti2.git
cd forseti2
git checkout 2016
cd ..

# get daemon
git clone https://github.com/rjli13/daemon.git
cd daemon
git checkout field-control
cd ..

# get lcm
sudo apt-get install -y build-essential
sudo apt-get install -y libglib2.0-dev
sudo apt-get install -y python-dev
wget https://github.com/lcm-proj/lcm/releases/download/v1.3.1/lcm-1.3.1.zip
unzip lcm-1.3.1
cd lcm-1.3.1
./configure
make
sudo make install
sudo ldconfig

# set up forseti2
cd ../forseti2
./gen-types.sh

# set up daemon
cd ../daemon/dawn
sudo npm install -g electron-prebuilt
sudo npm install
npm run-script build
cd

echo "Driver station deployed"