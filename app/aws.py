from flask import render_template, request, Flask
import pymysql as mdb
from model import read_url, flag_score, flag_score_post, parse_post, get_bag_words
from sql_statements import select_query_zip, select_query_full
import threetaps



API_KEY = '082906284971364c1cb52da644536e37'
DICT_FIELDS = ['id', 'source', 'category', 'category_group', 'location',
               'external_url', 'heading', 'body',
               'price', 'currency', 'images', 'flagged_status']
LOC_FIELDS = ['country', 'city', 'zipcode']
RETVALS = ['id', 'account_id', 'source', 'category', 'category_group', 'location',
           'external_id', 'external_url', 'heading', 'body', 'timestamp', 'timestamp_deleted',
           'expires', 'language', 'price', 'currency', 'images', 'annotations', 'status',
           'state', 'immortal', 'deleted', 'flagged_status']


client = threetaps.Threetaps(API_KEY)


app = Flask(__name__)


@app.route('/')
@app.route('/home')
def index():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")

# TODO Error pages for listings without MAPS
@app.route("/result")
def result_page():
    url = request.args.get('url')
    post, zipcode, post_id = read_url(url)
    score = flag_score(url)
    words = get_bag_words()
    response = client.search.search(params={'source': 'CRAIG',
                                            'retvals': ','.join(RETVALS),
                                            'sort': 'timestamp',
                                            'external_id': post_id
                                            })
    api_response = parse_post(response, DICT_FIELDS, LOC_FIELDS)

    if 'postings' not in response or response['postings'] == []:
        query_results = client.search.search(params={'source': 'CRAIG',
                                        'retvals': ','.join(RETVALS),
                                        'sort': 'timestamp',
                                        'location.zipcode': zipcode,
                                        'rpp': 100,
                                        })
    else:
        query_results = client.search.search(params={'source': 'CRAIG',
                                        'retvals': ','.join(RETVALS),
                                        'sort': 'timestamp',
                                        'category': api_response[0]['category'],
                                        'location.zipcode': api_response[0]['zipcode'],
                                        'category_group': api_response[0]['category_group'],
                                        'rpp': 25
                                        })

    flag_results = [dict(heading=result['heading'],
                                     body=result['body'], url=result['external_url'],
                                     flag_score=flag_score_post(result['body']))
                    for result in query_results['postings']]

    flag_results_sorted = sorted(flag_results, key=lambda k: k['flag_score'])
    return render_template('result.html', flag_results=flag_results_sorted, post=post,
                           score=str(score), WORDS=words)

if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=True)