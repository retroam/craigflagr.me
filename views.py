from flask import render_template, request
from app import app
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


db = mdb.connect(user="root", host="localhost", db="INSIGHTdb",
                 charset='utf8')
client = threetaps.Threetaps(API_KEY)




@app.route('/')
@app.route('/home')
def index():
    return render_template("home.html")

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
    with db:
        cur = db.cursor()
        if 'postings' not in response or response['postings'] == []:
            cur.execute(select_query_zip, zipcode)
        else:
            api_response = parse_post(response, DICT_FIELDS, LOC_FIELDS)
            cur.execute(select_query_full.format(api_response[0]['zipcode'],
                                                 api_response[0]['category'],
                                                 api_response[0]['category_group']))

        query_results = cur.fetchall()

    flag_results = []
    for result in query_results:
        flg_score = flag_score_post(result[2])
        flag_results.append(dict(heading=result[0], flagged_status=result[1],
                                 body=result[2], url=result[3],
                                 flag_score=flg_score))

    flag_results_sorted = sorted(flag_results, key=lambda k: k['flag_score'])
    return render_template('result.html', flag_results=flag_results_sorted, post=post,
                           score=str(score), WORDS=words)

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = error.to_dict()
    message = response.get('message', '')
    return render_template('error.html', message = message)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', message = "Page Not Found (404).")

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', message = "An unexpected error has occurred (500).")

