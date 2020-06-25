#!/usr/bin/python

import math
import numpy
import time
import re
import requests
from bs4 import BeautifulSoup

#Dictionary to store words and its frequency(One-to-one correspondence)
word_d = {}

#a list to store vector
vector_list = []

#a list to store urls
url_list = []

#a list to store cosine similarity
cossimil = []

#a set required to calculate tf-idf value
bow = set()

#a list for storing words for each url
word_list = []

def check_duplicate(_list):
	temp = 0
	if sorted(set(_list)) == sorted(_list):
		temp = 1
	return temp

def compute_tf(words):
	temp = set()
	temp_wordcount = {}
	
	for word in words:
		if word not in temp_wordcount.keys():
			temp_wordcount[word] = 0
		temp_wordcount[word] += 1
		temp.add(word)
	
	tf_d = {}
	
	for word, count in temp_wordcount.items():
		tf_d[word] = count / len(bow)
	
	return tf_d

def compute_idf():
	Dval = len(url_list)
	idf_d = {}
	
	for t in bow:
		cnt = 0
		for words in word_list:
			if t in words:
				cnt += 1
		idf_d[t] = numpy.log(Dval/cnt)
	
	return idf_d

def make_word_d(url = None):
	temp_list = []
	start = time.time()
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	
	for script in soup(["script", "style"]):
		script.extract()
	
	text = str(soup.get_text())
	text = re.sub(r'\'', '', text)
	text = re.sub('[^\s^A-Za-z0-9]', '', text)
	
	for word in text.split():
		if word not in word_d.keys():
			word_d[word] = 0
		word_d[word] += 1
		bow.add(word)
		temp_list.append(word)
	print("{ url } : ", url, "  { number of words } : ", len(temp_list), "  { time(second) } : ", time.time() - start)
	word_list.append(temp_list)

def crawl_multiple(_list = None):

	#Dictionary to store url and cosine similarity(One-to-one correspondence)
	url_cossimil = {}

	#Dictionary to store word and tf-idf value
	tfidf = {}
	
	for url in _list:
		url_list.append(url)
		#build word_d dictionary and word_list list
		make_word_d(url)

	#check duplicates
	if check_duplicate(url_list) == 0:
		print("\nDuplicate url found.")
	else:
		print("\nNo duplicates.")

	for url in _list:
		#multi_crawl_every_words : A function that produces vector by crawling its parameter url
		v = multi_crawl_every_words(url)
		vector_list.append(v)
	
	#user input
	index = int(input("\nInput index >> "))

	#calculate cosine similarity value
	for vector in vector_list:
		dotpro = numpy.dot(vector, vector_list[index])
		norms = numpy.linalg.norm(vector) * numpy.linalg.norm(vector_list[index])
		result = dotpro / norms
		cossimil.append(result)

	#store url and cosine similarity values in url_cossimil dictionary	
	for i in range(0, len(cossimil)):
		if i == index:
			continue
		url_cossimil[url_list[i]] = cossimil[i]

	#sort in descending order
	url_cos_dict = sorted(url_cossimil.items(), key = lambda t : t[1], reverse = True)

	#print top 3 urls by cosine similarity values
	count = 0
	for _data in url_cos_dict:
		print(_data, "(url , cosine similarity)")
		count+=1
		if(count==3):
			break

	#calculate tf-idf value
	idf_d = compute_idf()
	tf_d = compute_tf(word_list[index])
	
	#store words and its tf-idf value in tfidf dictionary
	for word, tfval in tf_d.items():
		tfidf[word] = tfval*idf_d[word]
	
	#sort in descending order
	tfidf = sorted(tfidf.items(), key = lambda t : t[1], reverse = True)
	
	#print top 10 words by tf-idf values
	print("\nTop 10 words(Based on TF-IDF) : ")
	for i in range(0, 10):
		print(tfidf[i])
 
	#initialize the cossimil list and tfidf list ('sorted' function returns 'list')
	del cossimil[:]
	del tfidf[:]

def multi_crawl_every_words(url = None):
	dic = {}
	start = time.time()
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')

	for script in soup(["script", "style"]):
		script.extract()

	text = str(soup.get_text())
	text = re.sub(r'\'', '', text)
	text = re.sub('[^\s^A-Za-z0-9]', '', text)

	for word in text.split():
		if word not in dic.keys():
			dic[word] = 0
		dic[word] += 1
	
	#function that creates vector(same as pdf example)
	_v = make_vector(dic)
	return _v

def make_vector(dic = None):
	v = []
	for word in word_d.keys():
		val = 0
		for t in dic.keys():
			if t == word:
				val += 1
		v.append(val)
	
	return v

if __name__ == '__main__':
	
	#url list
	urllist = ['http://jackrabbit.apache.org/jcr/index.html','http://parquet.apache.org/','http://qpid.apache.org/','http://rya.apache.org/','http://unomi.apache.org/']
	crawl_multiple(urllist)
