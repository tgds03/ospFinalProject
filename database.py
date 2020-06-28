#!/usr/bin/python3

from elasticsearch import Elasticsearch
import math
import json
import numpy

class Document:

	def __init__(self, url:str):
		self.url = url
		self.word_freq = {
		# "word" : {
		# 	"count" : "value", 
		# 	"tfidf" : "value"
		# }
		}
		#in database, word_freq = [ {'word':(word), 'count':(value), 'tfidf':(value)} ]
		self.status = None
		self.crawl_time = 0
		self.word_count = 0
		self.cos_similarity = {
			"norm" : -1,
			"data" : {
				# "url" : "value"
			}
		}

	#record crawling, parsing time
	def record_time(self, time:float):
		self.crawl_time = time

	#record words to word_freq
	def insert_word(self, word:str, count:int):
		word = word.lower()
		self.word_freq[word] = {"count":count, "tfidf":-1}
		self.word_count += count

	def insert_words(self, wordlist:{str:int}):
		for word in wordlist.keys():
			self.insert_word(word, wordlist[word])


	#calculate tfidf, using total word freq in documentES
	def calculate_tfidf(self, documentES:'DocumentES'):
		for word in self.word_freq.keys():
			tf = self.calculate_tf(word)
			idf = self.calculate_idf(word, documentES)
			self.word_freq[word]['tfidf'] = tf * idf

	def calculate_tf(self, word:str):
		return self.word_freq[word]['count'] / self.word_count

	#to get document which has a word, search by using elasticsearch
	def calculate_idf(self, word:str, documentES:'DocumentES'):
		word = word.lower()	#term search work only lowercase
		
		searchBody = documentES.termSearchbody
		searchBody['query']['nested']['query']['bool']['must']['match']['word_freq.word'] = word
		docHasWordNum = 0
		while(docHasWordNum == 0):
			res = documentES.es.search(index='osp', body=searchBody, filter_path='hits.total.value')
			docHasWordNum = res['hits']['total']['value']
		return math.log10(len(documentES.total_info['url_list']) / docHasWordNum)


	#calculate vector (of word) norm. it will be stored in document
	def calculate_norm(self):
		values = [self.word_freq[word]['count'] for word in self.word_freq]
		self.cos_similarity['norm'] = numpy.linalg.norm(values)

	#calcultate similarity with another document(other).
	#this value is stored in document with other's url
	def calculate_similarity(self, other:'Document'):	#pep-0484) forward reference

		#initiate each vector's norm
		if self.cos_similarity['norm'] < 0: self.calculate_norm()
		if other.cos_similarity['norm'] < 0: other.calculate_norm()

		selfNorm = self.cos_similarity['norm']
		otherNorm = other.cos_similarity['norm']

		dotProduct = 0
		otherWordList = other.word_freq.keys()
		#only add product if word is in both docs
		#if word is not in either docs, product is 0.
		for word in self.word_freq.keys():
			if word in otherWordList:
				dotProduct += self.word_freq[word]['count'] * other.word_freq[word]['count']

		cosSimilarity = dotProduct / (selfNorm * otherNorm)
		self.cos_similarity['data'][other.url] = cosSimilarity
		other.cos_similarity['data'][self.url] = cosSimilarity
		return cosSimilarity

	#convert to instance <-> index query
	def convert_to_dict(self):
		data = {"word_freq":[], "word_count":self.word_count, "url":self.url, "cos_similarity":{"data":[], "norm":self.cos_similarity["norm"]}, "crawl_time":self.crawl_time, "status":self.status}
		for word in self.word_freq.keys():
			info = self.word_freq[word]
			data["word_freq"].append( {"word":word, "count":info['count'], 'tfidf':info['tfidf']} )
		for similarity in self.cos_similarity['data'].keys():
			data["cos_similarity"]["data"].append( {"url":similarity, "value":self.cos_similarity['data'][similarity]})
		return data

def convert_to_document(data:dict):
	doc = Document(data['url'])
	# doc.cos_similarity = data['cos_similarity']
	doc.word_freq = {}
	doc.crawl_time = data['crawl_time']
	doc.status = data['status']
	for info in data['word_freq']:
		doc.word_freq[info['word']] = {"count":info['count'], 'tfidf':info['tfidf']}
	doc.cos_similarity['norm'] = data['cos_similarity']['norm']
	for info in data['cos_similarity']["data"]:
		doc.cos_similarity['data'][info['url']] = info['value']
	return doc


class DocumentES(Elasticsearch):
	es :Elasticsearch
	doc_count = 0

	total_info = {
		"total_word_freq" : {
			# "word" : "count"
		},
		#in database, total_word_freq = [ {'word':(word), 'count':(value)} ]
		"total_word_kinds" : 0,
		"total_word_count" : 0,
		"url_list" : [],
	}
	termSearchbody = None

	def __init__(self, host:str = '127.0.0.1', port:str = '9200'):
		self.es = Elasticsearch([{'host':host, 'port':port}], timeout=30)
		self.init_index('total')
		self.init_index('osp')
		self.es.index(index='total', id='total', body=self.total_info)
		with open('ospMappings.json', 'r') as f:
			# mapping = {"document" : json.load(f)}
			mapping = json.load(f)
			self.es.indices.put_mapping(index='osp', body=mapping)
		with open('searchBody.json', 'r') as f:
			self.termSearchbody = json.load(f)
		# self.es.indices.put_settings(index='osp', body={"index.mapping.total_fields.limit": 5000})

	#used for initiating database
	def init_index(self, indexName:str):
		if self.es.indices.exists(index=indexName):
			self.es.indices.delete(index=indexName)
		self.es.indices.create(index=indexName)


	#record word info to total_word_freq
	def insert_word(self, word:str, count:int):
		word = word.lower()
		if word not in self.total_info["total_word_freq"]:
			self.total_info["total_word_freq"][word] = 0
			self.total_info["total_word_kinds"] += 1
		self.total_info["total_word_freq"][word] += count
		self.total_info["total_word_count"] += count

	def insert_words(self, wordlist:{str,int}):
		for word in wordlist.keys():
			self.insert_word(word, wordlist[word])


	#when deal with document, it required to convert type dict-Document
	#insert document to database
	def insert_document(self, doc:Document):
		# return self.es.create(index='osp', body=doc.convert_to_dict(), id=doc.url)
		return self.es.index(index='osp', body=doc.convert_to_dict(), id=doc.url)

	#load document from database
	def load_document(self, url:str)->Document:
		res = self.es.get(index='osp', doc_type='_doc', id=url)
		return convert_to_document(res['_source'])


	#update total data in database
	def update_total(self):
		data = {"total_word_kinds":self.total_info["total_word_kinds"], "total_word_count":self.total_info["total_word_count"], "url_list":self.total_info["url_list"]}
		data["total_word_freq"] = []
		for word in self.total_info["total_word_freq"].keys():
			data["total_word_freq"].append({"word" : word, "count" : self.total_info["total_word_freq"][word]})
		return self.es.index(index='total', body=data, id='total')

	#load total data in database
	def load_total(self):
		res = self.es.get(index = 'total', id = 'total', filter_path='_source')
		res = res['_source']
		self.total_info["total_word_kinds"] = res["total_word_kinds"]
		self.total_info["total_word_count"] = res["total_word_count"]
		self.total_info["url_list"] = res["url_list"]
		self.total_info["total_word_freq"] = {}
		for word in res["total_word_freq"]:
			self.total_info["total_word_freq"][word["word"]] = word["count"]


from single_url_crawl import single_url_crawl

if __name__=="__main__":
	doc_es = DocumentES()
	urllist = ['http://jackrabbit.apache.org/jcr/index.html','http://parquet.apache.org/','http://qpid.apache.org/','http://rya.apache.org/','http://unomi.apache.org/', 'https://sites.google.com/site/teleoliseuteu/']
	documents = [Document(url) for url in urllist]
	
	#crawl received urls
	#maybe it will be executed as soon as receiving urls
	for doc in documents:
		crawled = single_url_crawl(doc.url)
		wordfreq = crawled['data']
		doc.insert_words(wordfreq)
		doc.record_time(crawled['time'])
		doc_es.insert_words(wordfreq)
		doc_es.total_info['url_list'].append(doc.url)
		doc_es.insert_document(doc)

	doc_es.update_total()
	doc_es.load_total()
	doc_es.update_total()

	#update urls similarity, tf-dif
	#maybe it will be executed by click buttons 
	for doc in documents:
		doc.calculate_tfidf(doc_es)
		for otherDoc in documents:
			if doc == otherDoc: continue
			doc.calculate_similarity(otherDoc)
		doc_es.insert_document(doc)

	print( "input index > ")
	doc = doc_es.load_document(urllist[int(input())])
	print( doc.word_freq )
	print( doc.cos_similarity )
