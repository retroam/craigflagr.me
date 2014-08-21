import threetaps
import json
from os import listdir

API_KEY = '082906284971364c1cb52da644536e37'
client = threetaps.Threetaps(API_KEY)

RETVALS = ['id', 'account_id', 'source', 'category', 'category_group', 'location',
           'external_id', 'external_url', 'heading', 'body', 'timestamp', 'timestamp_deleted',
           'expires', 'language', 'price', 'currency', 'images', 'annotations', 'status',
           'state', 'immortal', 'deleted', 'flagged_status']

FILE_PATH = '/home/ubuntu/data_dump'

number_files = 10000

files = listdir(FILE_PATH)
page = 0

response = client.search.search(params={'source': 'CRAIG',
                                            'retvals': ','.join(RETVALS),
                                            'sort': 'timestamp',
                                            'status': 'for_rent',
                                            'rpp': 1,
                                            'page': page})

ANCHOR = response['anchor']
for i in range(number_files):
    print str(page)
    response = client.search.search(params={'source': 'CRAIG',
                                            'retvals': ','.join(RETVALS),
                                            'sort': 'timestamp',
                                            'status': 'for_rent',
                                            'category_group': 'RRRR',
                                            'anchor': str(ANCHOR),
                                            'rpp': 100,
                                            'page': page})
    name = FILE_PATH + '/File0' + str(page) + '.json'
    with open(name, 'w') as outfile:
        json.dump(response, outfile)
    page += 1
