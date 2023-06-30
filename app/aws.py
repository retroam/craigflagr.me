from flask import Flask, render_template, request
from requests.exceptions import MissingSchema
import pymysql as mdb
from bs4 import BeautifulSoup
import requests
from model import read_url, flag_score, flag_score_post, parse_post, get_bag_words
from sql_statements import select_query_zip, select_query_full



DICT_FIELDS = ['id', 'source', 'category', 'category_group', 'location',
               'external_url', 'heading', 'body', 'price', 'currency', 
               'images', 'flagged_status']

LOC_FIELDS = ['country', 'city', 'zipcode']

RETVALS = ['id', 'account_id', 'source', 'category', 'category_group', 'location',
           'external_id', 'external_url', 'heading', 'body', 'timestamp', 
           'timestamp_deleted', 'expires', 'language', 'price', 'currency', 
           'images', 'annotations', 'status', 'state', 'immortal', 'deleted', 
           'flagged_status']



app = Flask(__name__)

@app.route('/')
@app.route('/home')
def index():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route("/result")
def result_page():
    url = request.args.get('url')
    post, zipcode, post_id = read_url(url)
    score = flag_score(url)
    words = get_bag_words()

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # assuming parse_post, flag_score_post, etc. are updated to work with BeautifulSoup objects
    api_response = parse_post(soup, DICT_FIELDS, LOC_FIELDS)


    # use BeautifulSoup to find similar posts based on the original post's details
    if api_response is None or api_response == []:
        query_results = search_similar_posts(zipcode)
    else:
        price_range = f"{api_response[0]['price'] - 500}..{api_response[0]['price'] + 500}"
        query_results = search_similar_posts(api_response[0]['zipcode'], api_response[0]['category'], price_range)

    flag_results = [dict(heading=result['heading'], body=result['body'], 
                         url=result['external_url'], flag_score=flag_score_post(result['body']))
                    for result in query_results]

    flag_results_sorted = sorted(flag_results, key=lambda k: k['flag_score'])

    return render_template('result.html', flag_results=flag_results_sorted, 
                           post=post, score=str(score), WORDS=words)
@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', message="Page not found")

@app.errorhandler(MissingSchema)
def url_not_found(error):
    return render_template('error.html', message="No URL entered")

@app.errorhandler(IndexError)
def post_not_found(error):
    return render_template('error.html', message="Check Craigslist post")

@app.errorhandler(500)
def server_error(error):
    return render_template('error.html', message="Server error")

def build_common_params(params):
    common_params = {
        'source': params.get('source'),
        'retvals': ','.join(RETVALS),
        'sort': 'timestamp'
    }
    return {**common_params, **params}

def search_postings(params):
    return client.search.search(params=build_common_params(params))

if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=True)
