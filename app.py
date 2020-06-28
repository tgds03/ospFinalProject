#!/usr/bin/python3

from flask import Flask
from flask import render_template
from flask import request

import database as db
import single_url_crawl as crawls
import re, sys

try:
	app = Flask(__name__)
	total_es = db.DocumentES()
except Exception as e:
	sys.exit('초기화 실패. flask 설치 또는 elasticsearch 실행을 확인하세요.')
urls = []
documents = []

def generate_listdata():
	return [{"idx":str(i+1), "url":d.url, "time":d.crawl_time, "count":d.word_count, "status":d.status} for i, d in enumerate(documents)]

@app.route('/')
def index():
	return render_template('osp.html')

@app.route('/addurl', methods=['POST'])
def addurl():
	url = request.form['homepage']
	url = re.sub(r'\s+', '', url)
	error = []
	if url == '':
		error.append('none')
	elif url in urls:
		error.append('duplicate')
	else :
		doc = db.Document(url)

		urls.append(url)
		documents.append(doc)

		#record url status
		try:
			crawled = crawls.single_url_crawl(url)
		except Exception as e:
			doc.status = str(e)
			doc.status = doc.status[0:30]+"..."
		
		#if url is accessible, record result
		if doc.status == None:
			wordfreq = crawled['data']
			doc.insert_words(wordfreq)
			doc.record_time(crawled['time'])

			total_es.insert_words(wordfreq)
			total_es.total_info['url_list'].append(doc.url)
			total_es.insert_document(doc)
			total_es.update_total()
	

	return render_template('osp.html', data=generate_listdata(), error=error)

@app.route('/addurls', methods=['POST'])
def addurls():
	new_urls = request.form['urls'].split(',')
	for url in new_urls:
		url = re.sub(r'\s+', '', url)
		if url == '' or url in urls: continue

		doc = db.Document(url)
		urls.append(url)
		documents.append(doc)

		#record url status
		try:
			crawled = crawls.single_url_crawl(url)
		except Exception as e:
			doc.status = str(e)
			doc.status = doc.status[0:30]+"..."
		
		#if url is accessible, record result
		if doc.status == None:
			wordfreq = crawled['data']
			doc.insert_words(wordfreq)
			doc.record_time(crawled['time'])

			total_es.insert_words(wordfreq)
			total_es.total_info['url_list'].append(doc.url)
			total_es.insert_document(doc)
			total_es.update_total()
	
	#print recorded until now
	return render_template('osp.html', data=generate_listdata())

@app.route('/similar', methods=['POST'])
def print_similar():
	docIdx = request.form['idx']
	doc = documents[int(docIdx)-1]
	if doc.status != None: 
		return render_template('similar_analysis_pop.html', data=(doc.url, []))
	cosSimil = []
	for i, otherdoc in enumerate(documents):
		if doc == otherdoc or otherdoc.status!=None: continue
		sim = doc.calculate_similarity(otherdoc)
		total_es.insert_document(otherdoc)
		cosSimil.append( (i+1, otherdoc.url, sim))
	total_es.insert_document(doc)

	cosSimil = sorted(cosSimil, key=lambda x : -x[2])
	return render_template('similar_analysis_pop.html', data=(doc.url, cosSimil[0:3]))

@app.route('/analysis', methods=['POST'])
def print_analysis():
	docIdx = request.form['idx']
	doc = documents[int(docIdx)-1]
	if doc.status != None: 
		return render_template('word_analysis_pop.html', data=(doc.url, []))
	doc.calculate_tfidf(total_es)

	wordfreq = []
	for word in doc.word_freq.keys():
		wordfreq.append( (word, doc.word_freq[word]['tfidf']) )
	wordfreq= sorted(wordfreq, key=lambda x: -x[1] )

	res = [ {"rank":i, "word":wordfreq[i][0], "tfidf":wordfreq[i][1]} for i in range(min(len(wordfreq), 10)) ]
	return render_template('word_analysis_pop.html', data=(doc.url, res))


if __name__=="__main__":  	app.run(debug=True)
