#!/bin/bash

sudo apt-get install python3-pip
sudo pip3 install flask
sudo pip3 install numpy
sudo pip3 install time
sudo pip3 install requests
sudo pip3 install bs4

mkdir -p ospFinalProject/templates
//tar -zxvf FILENAME.tar.gz -C /ospFinalProject     FILENAME에 파일 이름 추가하기
cd ospFinalProject
mv osp.html similar_analysis_pop.html word_analysis_pop.html ospFinalProject/templates
sudo service elasticsearch start
cd ../ospFinalProject
sudo chmod 755 app.py
python ./app.py
