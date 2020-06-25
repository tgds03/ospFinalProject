#!/usr/bin/python

import time
import re
import requests
from bs4 import BeautifulSoup

def single_url_crawl(url=None):

	#a list to include words in html(allow duplication)
	word_info = {}
	word_count = 0
	
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
	text = re.sub(r'[^\s^A-Za-z0-9]', '', text)
	text = text.split()

	for word in text:
		word_info[word] = text.count(word)
		word_count += word_info[word]

	print("\nNumber of words : ", len(word_info), end='\n')
	print(word_info)

	#The 'time.time()' (current time) minus 'start' is the execution time
	print("\ncrawl time(second) : {0:0.2f}".format(time.time()-start))

	return word_info

if __name__ == '__main__':
	url = input("Input url(Any url!) : ")
	single_url_crawl(url)
