from elasticsearch import Elasticsearch
import numpy

class Document:
	word_freq = {
		# "word" : {
		# 	"count" : "value", 
		# 	"tfidf" : "value"
		# }
	}
	url = ''
	cos_similarity = {
		"norm" : -1,
		"data" : {
			# "url" : "value"
		}
	}

	def __init__(self, url:str):
		self.url = url

	def insert_word(self, word:str, count:int, tfidf:float):
		self.word_freq[word] = {"count":count, "tfidf":tfidf}

	#calculate vector (of word) norm. it will be stored in document
	def calculate_norm(self):
		self.cos_similarity['norm'] = numpy.linalg.norm([word['count'] for word in self.word_freq])

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

	def convert_to_dict(self):
		return {"word_freq":self.word_freq, "url":self.url, "cos_similarity":self.cos_similarity}

def convert_to_document(data:dict):
	doc = Document(data['url'])
	doc.word_freq = data['word_freq']
	doc.cos_similarity = data['cos_similarity']


class DocumentES(Elasticsearch):
	es :Elasticsearch
	doc_count = 0
	url_list = []

	total_info = {
		"total_word_freq" : {
			# "word" : "count"
		},
		"total_word_kinds" : 0,
		"total_word_count" : 0
	}

	def __init__(self, host:str = '127.0.0.1', port:str = '9200'):
		self.es = Elasticsearch([{'host':host, 'port':port}], timeout=30)
		self.init_index('total')
		self.init_index('osp')
		self.es.index(index='total', id='total', body=self.total_info)

	#used for initiating database
	def init_index(self, indexName:str):
		if self.es.indices.exists(index=indexName):
			self.es.indices.delete(index=indexName)
		self.es.indices.create(index=indexName)


	#when deal with document, it required to convert type dict-Document
	#insert document to database
	def insert_document(self, doc:Document):
		return self.es.index(index='osp', doc_type='document', body=doc.convert_to_dict(), id=doc.url)

	#load document from database
	def load_document(self, url:str)->Document:
		res = self.es.get(index='osp', id =url, filter_path='hits.hits')
		return convert_to_document(res['_source'])


	#update total data in database
	def update_total(self, data:dict):
		return self.es.index(index='total', body=data, id='total')

	#load total data in database
	def load_total(self):
		res = self.es.get(index = 'total', id = 'total', filter_path='_source')
		res = res['_source']
		self.total_info = res.copy()


if __name__=="__main__":
	es = DocumentES()
	testdoc = Document('https://www.naver.com')
	print(es.insert_document(testdoc))
	