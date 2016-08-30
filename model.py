import requests
from BeautifulSoup import BeautifulSoup
import pickle
from collections import defaultdict
from gmaps import Geocoding
import re
from math import ceil
import os


dir_path = os.path.dirname(os.path.realpath(__file__))

PICKLE_FILE = dir_path + '/data/craigslist_classifier.pickle'
f = open(PICKLE_FILE)
classifier = pickle.load(f)


def get_post_words(post, stopwords=[]):
    pwords = [w for w in post.split() if not w in stopwords]
    return pwords


def get_bag_words():
    words = []
    cpdist = classifier._feature_probdist
    for (fname, fval) in classifier.most_informative_features(10000):
        prob = cpdist['flag', fname].prob(fval)/cpdist['no_flag', fname].prob(fval)
        if prob > 2 and len(fname) > 2:
            words.append(fname)
    words_encode = [word.encode('utf-8') for word in words]
    return words_encode


def feature_extractor(post, list_words=[], stop_words=[]):
    features = defaultdict(list)
    post_word = get_post_words(post)
    if not list_words:
        for w in post_word:
            if w not in stop_words:
                features[w] = True
        return features
    else:
        for w in post_word:
            if w not in stop_words and w in list_words:
                features[w] = True
            return features


def text_clean(listing_text):
    listing_text_clean = re.sub('\n|\t', ' ', listing_text)
    listing_text_clean = re.sub('\s+', ' ', listing_text_clean)
    listing_text_clean = re.sub("'", '', listing_text_clean)
    listing_text_clean = re.sub('"', '', listing_text_clean)
    return listing_text_clean.lstrip().strip()


def get_zip(loc):
    try:
        latitude = loc[0].get('data-latitude')
        longitude = loc[0].get('data-longitude')
        google_api = Geocoding('AIzaSyBkWTcFg-kawvHmt1MryKvMcpmsNmrGWPU')
        map_loc = google_api.reverse(float(latitude), float(longitude))
        items = map_loc[0]['address_components']
        result = [item['long_name'] for item in items if item['types'][0] == 'postal_code']
        code = 'USA-' + result[0]
        return code
    except IndexError:
        return None


def read_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text)
    find_section = soup.findAll('section', attrs={"id": "postingbody"})
    text = find_section[0].findAll(text=True)
    clean_text = text_clean(' '.join(text))

    find_loc = soup.findAll('div', attrs={"id": "map"})
    zipcode = get_zip(find_loc)

    find_id = soup.findAll('p', attrs={"class": "postinginfo"})
    regex = r"[\S+]:\s(.\w+)"
    post_id = re.findall(regex, find_id[1].findAll(text=True)[0])

    return clean_text, zipcode, post_id


def flag_score(url):
    post, _, _ = read_url(url)
    result = classifier.prob_classify(feature_extractor(post))
    score = int(ceil(result.prob('flag')*100))
    return score


def flag_score_post(post):
    result = classifier.prob_classify(feature_extractor(post))
    score = int(ceil(result.prob('flag')*100))
    return score


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

