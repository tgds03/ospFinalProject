#!/usr/bin/python

import time
import re
import requests
from bs4 import BeautifulSoup

def single_url_crawl(url=None):

	#a list to include words in html(allow duplication)
	lists = []
	
	#crawling time measurement
	start = time.time()
	
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')

	#Remove all style, scripts tag in html
	for script in soup(["script", "style"]):
		script.extract()
	
	text = str(soup.get_text())
	
	#extract words in text
	text = re.sub(r'\'', '', text)
	text = re.sub('[^\s^A-Za-z0-9]', '', text)

	for word in text.split():
		lists.append(word)

	print("\nNumber of words : ", len(lists))

	#The 'time.time()' (current time) minus 'start' is the execution time
	print("\ncrawl time(second) : {0:0.2f}".format(time.time()-start))

if __name__ == '__main__':
	url = input("Input url(Any url!) : ")
	single_url_crawl(url)
