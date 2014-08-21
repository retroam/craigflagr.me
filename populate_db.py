import pymysql as mdb
from os import listdir
import json
import requests
from BeautifulSoup import BeautifulSoup


FILE_PATH = '/home/ubuntu/data_dump'
INITIALIZE = True
drop_table_sql = '''
                   DROP TABLE IF EXISTS Recommendations
                   '''

create_table_sql = '''
                   CREATE TABLE Recommendations (
                   id INTEGER,
                   source TEXT,
                   category TEXT,
                   category_group TEXT,
                   country TEXT,
                   city TEXT,
                   zipcode TEXT,
                   external_url TEXT,
                   heading TEXT,
                   body TEXT,
                   price INTEGER,
                   currency TEXT,
                   images INTEGER,
                   flagged_status INTEGER

                   )
                   '''

create_index_sql = '''
                   CREATE INDEX column_id
                   ON Recommendations (id)
                   '''

populate_index_sql = '''
                     INSERT INTO Recommendations VALUES(
                     %(id)s,
                     %(source)s,
                     %(category)s,
                     %(category_group)s,
                     %(country)s,
                     %(city)s,
                     %(zipcode)s,
                     %(external_url)s,
                     %(heading)s,
                     %(body)s,
                     %(price)s,
                     %(currency)s,
                     %(images)s,
                     %(flagged_status)s
                     )
                     '''
dict_fields = ['id', 'source', 'category', 'category_group', 'location',
               'external_url', 'heading', 'body',
               'price', 'currency', 'images', 'flagged_status']

location_fields = ['country', 'city', 'zipcode']

test_select_sql = '''
                   SELECT *
                   FROM Recommendations
                     '''


def parse_post(data, dict_fields, location_fields):
    parsed_posts = []
    for i in range(len(data['postings'])):
        my_dict = {}
        for field in dict_fields:
            if field == 'location':
                for location_field in location_fields:
                    if location_field in data['postings'][i]['location']:
                        my_dict[location_field] = data['postings'][i][field][location_field]
                    else:
                        my_dict[location_field] = None
            elif field == 'images':
                 my_dict[field] = len(data['postings'][i][field])
            elif field == 'external_url':
                    my_dict[field] = mdb.escape_string(data['postings'][i][field])
            elif field == 'flagged_status':
                url = data['postings'][i]['external_url']
                #my_dict[field] = check_flag(url)
                my_dict[field] = 2
            elif field in data['postings'][i]:
                my_dict[field] = data['postings'][i][field]
            else:
                 my_dict[field] = None
        parsed_posts.append(my_dict)

    return parsed_posts


def check_flag(post_url):
    flag_message = 'This posting has been flagged for removal.[?]'
    try:
        response = requests.get(post_url)
        soup = BeautifulSoup(response.text)
        tag = soup.find('h2').text
        if tag == flag_message:
            return 1
        else:
            return 0
    except:
        return 2

con = mdb.connect('localhost', 'root', '', 'INSIGHTdb', charset='utf8')

files = listdir(FILE_PATH)
if '.DS_Store' in files: files.remove('.DS_Store')


if INITIALIZE:
    with con:
        cur = con.cursor()
        cur.execute(drop_table_sql)
        cur.execute(create_table_sql)
        cur.execute(create_index_sql)


with con:
    cur = con.cursor()
    for file in files:
        try:
            with open(FILE_PATH + '/' + file) as f:
                print FILE_PATH + '/' + file
                data = parse_post(json.load(f), dict_fields, location_fields)
                for j in range(len(data)):
                    cur.execute(populate_index_sql, data[j])
                    con.commit()
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)

with con:
    cur = con.cursor()
    cur.execute(test_select_sql)

print cur.fetchall()