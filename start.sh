#!/bin/bash

sudo apt-get install python3-pip
sudo pip install flask
sudo pip install re
sudo pip install sys
sudo pip install math
sudo pip install json
sudo pip install numpy
sudo pip install time
sudo pip install requests
sudo pip install bs4

mkdir -p ospFinalProject/templates
tar -zxvf 압축파일명.tar.gz -C /ospFinalProject	//ospFinalProject 디렉토리에 압축 풀기
cd ospFinalProject
mv osp.html similar_analysis_pop.html word_analysis_pop.html ospFinalProject/templates/
./elasticsearch-7.6.2/bin/elasticsearch -d
sudo chmod 755 app.py
./app.py

