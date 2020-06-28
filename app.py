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
			doc.status = doc.status[0:doc.status.find(":")]
		
		#if url is accessible, record result
		if doc.status == None:
			wordfreq = crawled['data']
			doc.insert_words(wordfreq)
			doc.record_time(crawled['time'])

			total_es.insert_words(wordfreq)
			total_es.total_info['url_list'].append(doc.url)
			total_es.insert_document(doc)
			total_es.update_total()
	
	data = [{"url":d.url, "time":d.crawl_time, "count":d.word_count, "status":d.status} for d in documents]

	return render_template('osp.html', data=data, error=error)

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
			doc.status = doc.status[0:doc.status.find(":")]
		
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
	data = [{"url":d.url, "time":d.crawl_time, "count":d.word_count, "status":d.status} for d in documents]
	return render_template('osp.html', data=data)

# @app.route('/similar', method=['POST'])
# def print_similar():

# @app.route('/analysis', method=['POST'])
# def print_analysis():

if __name__=="__main__": app.run(debug=True)