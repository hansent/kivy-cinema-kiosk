#!/bin/bash

try () {
    "$@" || exit -1
}

if [ ! -d zeromq ]; then
	mkdir zeromq
fi

try cd zeromq

# install ZEROMQ 
# (DEFAUTL INSTALL is into /usr/local/lib, so LD_LIBRARY_PATH must be set
# to include this when runngin exectables)
pkg-config uuid
if [ $? -ne 0 ]; then
	sudo apt-get -y install uuid-dev
fi

try wget http://www.zeromq.org/local--files/area:download/zeromq-2.0.10.tar.gz
try tar -xzvf zeromq-2.0.10.tar.gz
try cd zeromq-2.0.10
try ./configure
try make
try sudo make install

cd ..

# install pyzmq
try wget --no-check-certificate  https://github.com/zeromq/pyzmq/downloads/pyzmq-2.0.10.1.tar.gz
try tar -xzvf pyzmq-2.0.10.1.tar.gz
try cd pyzmq-2.0.10.1
try cp setup.cfg.template setup.cfg
try sudo python setup.py install

cd ../..
sudo rm -rf zeromq

