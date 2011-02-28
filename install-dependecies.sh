#!/bin/bash

mkdir zeromq
cd zeromq

#install ZEROMQ  (DEFAUTL INSTALL is into /usr/local/lib, so LD_LIBRARY_PATH must be set to include this when runngin exectables)
cd zeromq
sudo apt-get -y install uuid
wget http://www.zeromq.org/local--files/area:download/zeromq-2.0.10.tar.gz
tar -xzvf zeromq-2.0.10.tar.gz
cd zeromq-2.0.10
./configure
make
sudo make install
cd ..

#install pyzmq
wget --no-check-certificate  https://github.com/zeromq/pyzmq/downloads/pyzmq-2.0.10.1.tar.gz
tar -xzvf pyzmq-2.0.10.1.tar.gz
cd pyzmq-2.0.10.1
cp setup.cfg.template setup.cfg
sudo python setup.py install

cd ../..
sudo rm -rf zeromq
 
