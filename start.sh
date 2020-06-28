#!/bin/bash

sudo apt-get install python3-pip
sudo pip3 install flask
sudo pip3 install numpy
sudo pip3 install requests
sudo pip3 install bs4

tar -zxvf ospFinalProject.tar.gz -C ./

sudo service elasticsearch start
cd ospFinalProject/
sudo chmod 755 app.py
flask run
