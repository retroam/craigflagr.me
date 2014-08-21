import threetaps
import json
from os import listdir

API_KEY = '082906284971364c1cb52da644536e37'
client = threetaps.Threetaps(API_KEY)

ANCHOR = 1281205933

RETVALS = ['id', 'account_id', 'source', 'category', 'category_group', 'location',
           'external_id', 'external_url', 'heading', 'body', 'timestamp', 'timestamp_deleted',
           'expires', 'language', 'price', 'currency', 'images', 'annotations', 'status',
           'state', 'immortal', 'deleted', 'flagged_status']

FILE_PATH = '/data_dump'

number_files = 10000

files = listdir(FILE_PATH)


def file_num(a):
    return int(a[5:-5])
files_trunc = files[1:]

last_file = sorted(files_trunc, key=file_num)[-1]
print last_file
with open(FILE_PATH + '/' + last_file) as f:
        my_dict = json.load(f)
        next_page = my_dict['next_page']

page = next_page
print next_page

for i in range(number_files):
    print str(page)

    response = client.search.search(params={'source': 'CRAIG',
                                            'retvals':','.join(RETVALS),
                                            'sort': 'timestamp',
                                            'status': 'for_rent',
                                            'anchor': str(ANCHOR),
                                            'rpp': 100,
                                            'page': page})
    name = FILE_PATH + '/File0' + str(page) + '.json'
    with open(name, 'w') as outfile:
        json.dump(response, outfile)
    page += 1
