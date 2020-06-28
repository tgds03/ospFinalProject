#!/bin/bash

sudo apt-get install python3-pip
sudo pip3 install flask
sudo pip3 install numpy
sudo pip3 install requests
sudo pip3 install bs4

mkdir -p _ospFinalProject/templates
tar -zxvf temp.tar.gz -C _ospFinalProject
cd _ospFinalProject/test
mv osp.html similar_analysis_pop.html word_analysis_pop.html ../templates
mv single_url_crawl.py app.py database.py ospMappings.json searchBody.json ../
cd ..
rm -rf test 
cd ../elasticsearch-7.6.2
./bin/elasticsearch -d
cd ../_ospFinalProject
sudo chmod 755 app.py
./app.py
