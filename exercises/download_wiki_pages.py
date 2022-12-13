import os
import pickle
import sys
import time
import traceback
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

import ipdb

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/95.0.4638.54 Safari/537.36 RuxitSynthetic/1.0 v3029941779778713443 ' \
             't1946166402082625254 athf552e454 altpriv cvcv=2 smf=0'
ACCEPT = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
ACCEPT_ENCODING = None
HTTP_TIMEOUT = 5
HEADERS = {'User-Agent': USER_AGENT,
           'Accept': ACCEPT,
           'Accept-Encoding': ACCEPT_ENCODING,
           'Content-Encoding': 'gzip'}
DELAY_REQUESTS = 2
MAIN_DIRPATH = os.path.expanduser('~/data/wikipedia/')
SAVE_DIRPATH = os.path.join(MAIN_DIRPATH, 'method01')
LIST_PICKLE_FILENAME = 'list_physicists_urls.pkl'
BYTES_DOWNLOADED = 0
URLS_INFO = {'urls_status': {},
             'urls_processed': [],
             'pages_not_downloaded': set(),
             'images_not_downloaded': set()}
START_TIME = None


def get_response(session, url, headers, timeout):
    global BYTES_DOWNLOADED
    try:
        req = session.get(url, headers=headers, timeout=timeout)
    except requests.exceptions.ConnectionError as e:
        print(e)
        return None
    if req.headers.get('content-length'):
        bytes_downloaded = int(req.headers['content-length'])
    else:
        print("No 'content-length' found in headers")
        print('Computing content length with len(req.content)')
        bytes_downloaded = len(req.content)
    BYTES_DOWNLOADED += bytes_downloaded
    return req


def sleep():
    global START_TIME
    assert START_TIME is not None
    sleep_time = DELAY_REQUESTS - (time.time() - START_TIME)
    if sleep_time > 0:
        print(f'Sleeping for {round(sleep_time, 3)} second')
        time.sleep(sleep_time)


def download_image(session, page_url, tag):
    global START_TIME, URLS_INFO
    src_image = tag[0].find('img')['src']
    if src_image.startswith('//'):
        print('Image found in the Wikipedia page')
        url_image = 'http:' + src_image
        req = get_response(session, url_image, HEADERS, HTTP_TIMEOUT)
        START_TIME = time.time()
        if req is not None:
            filename = urlparse(url_image).path.split('/')[-1].split(':')[-1]
            filepath = os.path.join(SAVE_DIRPATH, filename)
            with open(filepath, 'wb') as f:
                f.write(req.content)
            URLS_INFO['urls_status'][page_url].setdefault('status_image', f'Image downloaded and saved: {filepath}')
            print('Image saved!')
        else:
            print(f"Image couldn't be downloaded: {url_image}")
            URLS_INFO['urls_status'][page_url].setdefault('status_image', f'ConnectionError: {url_image}')
            URLS_INFO['images_not_downloaded'].add(page_url)
    else:
        print(f'Unsupported image found in the Wikipedia page: {src_image}')
        URLS_INFO['urls_status'][page_url].setdefault('status_image', f'Unsupported image found: {src_image}')
        URLS_INFO['images_not_downloaded'].add(page_url)


def download_page(session, page_url):
    try:
        global START_TIME, URLS_INFO
        req = get_response(session, page_url, HEADERS, HTTP_TIMEOUT)
        START_TIME = time.time()
        if req is None:
            sleep()
            URLS_INFO['urls_status'][page_url].setdefault('status_page', 'ConnectionError')
            URLS_INFO['pages_not_downloaded'].add(page_url)
            return None
        html = req.text
    except OSError as e:
        URLS_INFO['urls_status'][page_url].setdefault('status_page', 'OSError')
        URLS_INFO['pages_not_downloaded'].add(page_url)
        return None
    if req.status_code == 404:
        print(f'404 - PAGE NOT FOUND: {page_url}')
        URLS_INFO['urls_status'][page_url].setdefault('status_page', '404 - PAGE NOT FOUND')
        URLS_INFO['pages_not_downloaded'].add(page_url)
    else:
        filename = urlparse(page_url).path.split('/')[-1] + '.html'
        filepath = os.path.join(SAVE_DIRPATH, filename)
        with open(filepath, 'w') as f:
            f.write(html)
        print('Wikipedia page saved!')
        URLS_INFO['urls_status'][page_url].setdefault('status_page', f'Page downloaded and saved: {filepath}')
    return req


def download_pages():
    global BYTES_DOWNLOADED, URLS_INFO, START_TIME
    filepath = os.path.join(MAIN_DIRPATH, LIST_PICKLE_FILENAME)
    req_session = requests.Session()
    print(f'Loading list of URLs: {filepath}')
    with open(filepath, 'rb') as f:
        list_physicists_urls = pickle.load(f)
    total_nb_urls = len(list_physicists_urls)
    print(f'Number of URLs: {total_nb_urls}')
    print()
    for i, page_url in enumerate(list_physicists_urls):
        print(f'processing url {i+1} of {total_nb_urls}: {page_url}')
        URLS_INFO['urls_status'].setdefault(page_url, {})
        URLS_INFO['urls_processed'].append(page_url)
        req = download_page(req_session, page_url)
        if req.status_code != 404:
            # Save image separately
            bs = BeautifulSoup(req.text, 'html.parser')
            td_tag = bs.select('.infobox-image')
            if td_tag:
                download_image(req_session, page_url, td_tag)
            else:
                print('No infobox-image found in the Wikipedia page')
                URLS_INFO['urls_status'][page_url].setdefault('status_image', 'No infobox-image found')
                print('Trying to find image in a `thumbinner` <div> class')
                a_tag = bs.select('.thumbinner > a')
                if a_tag:
                    download_image(req_session, page_url, a_tag)
                else:
                    print('No thumbinner-image found in the Wikipedia page')
                    URLS_INFO['urls_status'][page_url]['status_image'] += '; No thumbinner-image found'
                    URLS_INFO['images_not_downloaded'].add(page_url)
        sleep()
        print()


args = sys.argv
resume = False
if len(args) == 2 and args[1] == 'r':
    resume = True
results = None
try:
    download_pages()
except KeyboardInterrupt:
    print('\nDownload stopped!')
except Exception as e:
    print('Download interrupted')
    # err_msg = "{}: {}".format(str(e.__class__).split("'")[1], e)
    # print(err_msg)
    print(traceback.format_exc())
# number of bytes in a megabyte
ipdb.set_trace()
MBFACTOR = float(1 << 20)
print(f'Total bytes downloaded: {BYTES_DOWNLOADED} [{round(BYTES_DOWNLOADED/MBFACTOR, 2)} MB]')
