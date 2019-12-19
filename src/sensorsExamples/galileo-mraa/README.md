# soft-iot-tatu-python

Galileo linux is an older version which has no longer updates. Then, we need at least to update python 2.7 to a new version (we used version 2.7.17), in order to use some modules as requests module. Also, we did an update on pip.

Updating python:
	wget https://www.python.org/ftp/python/2.7.17/Python-2.7.17.tgz
	tar -xvzf Python-2.7.17.tgz
	cd Python-2.7.17
	./configure --prefix=/usr/local (it will take a while)
	x (it will take several minutes)
	cd /usr/bin
	unlink python
	alias python=python2.7.17
	link python2.7 python

Updating pip:
	pip install --upgrade pip

Installing python modules for TATU:
	pip install paho-mqtt
	pip install requests
	pip install -U Flask
