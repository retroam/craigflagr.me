import requests
from bs4 import BeautifulSoup
import pickle
from collections import defaultdict
import re
from math import ceil
from typing import List, Dict, Any, Tuple, Optional

PICKLE_FILE = '../app/data/craigslist_classifier.pickle'
with open(PICKLE_FILE, 'rb') as f:
    classifier = pickle.load(f)


def get_post_words(post: str, stopwords: Optional[List[str]] = None) -> List[str]:
    """Extract words from post which are not in the stopwords list."""
    stopwords = stopwords or []
    return [w for w in post.split() if not w in stopwords]


def get_bag_words() -> List[bytes]:
    """Get a bag of words from the most informative features of the classifier."""
    words = []
    cpdist = classifier._feature_probdist
    for (fname, fval) in classifier.most_informative_features(10000):
        prob = cpdist['flag', fname].prob(fval) / cpdist['no_flag', fname].prob(fval)
        if prob > 2 and len(fname) > 2:
            words.append(fname)
    return [word.encode('utf-8') for word in words]


def feature_extractor(post: str, list_words: Optional[List[str]] = None,
                      stop_words: Optional[List[str]] = None) -> Dict[str, bool]:
    """Extract features from the post using specified lists of words."""
    list_words = list_words or []
    stop_words = stop_words or []
    features = defaultdict(list)
    post_word = get_post_words(post)
    for w in post_word:
        if w not in stop_words and (not list_words or w in list_words):
            features[w] = True
    return features


def text_clean(listing_text: str) -> str:
    """Clean up the listing text by removing newlines, tabs, and extra spaces."""
    listing_text_clean = re.sub('\n|\t', ' ', listing_text)
    listing_text_clean = re.sub('\s+', ' ', listing_text_clean)
    listing_text_clean = re.sub("'", '', listing_text_clean)
    listing_text_clean = re.sub('"', '', listing_text_clean)
    return listing_text_clean.lstrip().strip()


def get_zip(loc: List[Any]) -> Optional[str]:
    """Get the ZIP code from the location information."""
    try:
        latitude = loc[0].get('data-latitude')
        longitude = loc[0].get('data-longitude')
        return f"USA-{latitude}{longitude}"
    except IndexError:
        return None


def read_url(url: str) -> Tuple[str, Optional[str], List[str]]:
    """Read the webpage at the URL and extract post, ZIP code, and post ID."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    find_section = soup.find_all('section', attrs={"id": "postingbody"})
    text = find_section[0].get_text()
    clean_text = text_clean(text)

    find_loc = soup.find_all('div', attrs={"id": "map"})
    zipcode = get_zip(find_loc)

    find_id = soup.find_all('p', attrs={"class": "postinginfo"})
    regex = r"[\S+]:\s(.\w+)"
    post_id = re.findall(regex, find_id[1].get_text())

    return clean_text, zipcode, post_id


def flag_score(url: str) -> int:
    """Calculate the flag score for the post at the URL."""
    post, _, _ = read_url(url)
    result = classifier.prob_classify(feature_extractor(post))
    score = int(ceil(result.prob('flag')*100))
    return score


def flag_score_post(post: str) -> int:
    """Calculate the flag score for the post."""
    result = classifier.prob_classify(feature_extractor(post))
    score = int(ceil(result.prob('flag')*100))
    return score


def parse_post(data: Dict[str, Any], dict_fields: List[str], location_fields: List[str]) -> List[Dict[str, Any]]:
    """Parse the posts in the data using specified fields."""
    parsed_posts = []
    for posting in data['postings']:
        my_dict = {}
        for field in dict_fields:
            if field == 'location':
                for location_field in location_fields:
                    my_dict[location_field] = posting['location'].get(location_field, None)
            elif field == 'images':
                my_dict[field] = len(posting.get(field, []))
            elif field == 'external_url':
                my_dict[field] = mdb.escape_string(posting.get(field, ''))
            elif field == 'flagged_status':
                my_dict[field] = 2
            else:
                my_dict[field] = posting.get(field, None)
        parsed_posts.append(my_dict)
    return parsed_posts
