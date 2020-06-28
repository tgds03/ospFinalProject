#!/bin/bash

sudo apt-get install python3-pip
sudo pip3 install flask
sudo pip3 install numpy
sudo pip3 install time
sudo pip3 install requests
sudo pip3 install bs4

mkdir -p ospFinalProject/templates
//tar -zxvf 압축파일명.tar.gz -C /ospFinalProject
cd ospFinalProject
mv osp.html similar_analysis_pop.html word_analysis_pop.html ospFinalProject/templates
cd ../elasticsearch-7.6.2
./bin/elasticsearch -d
cd ../ospFinalProject
python app.py
sudo chmod 755 app.py
./app.py