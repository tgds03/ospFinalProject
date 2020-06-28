from flask import Flask
from flask import render_template
from flask import redirect, url_for, request
import database as db
from single_url_crawl import single_url_crawl as suc

app = Flask(__name__)

url_list=[]

_dict = {
            'url' : {
                    #url
            },
            'time' : {
                    #time
            },
            'count': {
                    #count
            }
}

@app.route('/')
def home(homepage=None):
    return render_template('osp_2.html')


#@app.route('/result/<list=url_list>/')
#def _result(url_list = None):
#    for homepage in url_list:
#        temp_class = db.Document(homepage)
#        crawled = suc(homepage)
#        wordfreq = crawled['data']
#        temp_class.insert_words(wordfreq)
#        temp_class.record_time(crawled['time'])
#        _dict['url'] = homepage
#        _dict['time'] = temp_class.crawl_time
#        _dict['count'] = temp_class.word_count

#    return render_template('osp_1.html', data = _dict)


@app.route('/addurl', methods=['POST'])
def add_url_to_list(homepage=None):
    flag = 1
    _homepage = request.form['homepage']
    url_list.append(_homepage)
    temp_class = db.Document(_homepage)
    if(temp_class == None):
        flag = -1
    crawled = suc(_homepage)
    wordfreq = crawled['data']
    temp_class.insert_words(wordfreq)
    temp_class.record_time(crawled['time'])
    url = str(_homepage)
    time= temp_class.crawl_time
    count = temp_class.word_count

    return render_template('osp_2.html', n = flag, _url = url, _time = time, _count = count)


if __name__ == '__main__':
    app.run(debug=True)




