from flask import Flask
from flask import render_template
from flask import request

import database as db
import single_url_crawl as crawls
import re

app = Flask(__name__)
total_es = db.DocumentES()
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
	if url == None:
		error.append('none')
	elif url in urls:
		error.append('duplicate')
	else :
		doc = db.Document(url)

		urls.append(url)
		documents.append(doc)

		crawled = crawls.single_url_crawl(url)
		wordfreq = crawled['data']
		doc.insert_words(wordfreq)
		doc.record_time(crawled['time'])

		total_es.insert_words(wordfreq)
		total_es.total_info['url_list'].append(doc.url)
		total_es.insert_document(doc)
		total_es.update_total()
	
	data = [{"url":d.url, "time":d.crawl_time, "count":d.word_count} for d in documents]

	return render_template('osp.html', data=data, error=error)

# @app.route('/similar', method=['POST'])
# def print_similar():

# @app.route('/analysis', method=['POST'])
# def print_analysis():

if __name__=="__main__":	app.run(debug=True)