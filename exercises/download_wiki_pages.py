import logging
import os
import pickle
import time
from logging import NullHandler
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
SAVE_DIRPATH = os.path.join(MAIN_DIRPATH, 'physicists')
LIST_PICKLE_FILENAME = 'list_physicists_urls.pkl'
BYTES_DOWNLOADED = 0
URLS_INFO = {'urls_status': {},
             'urls_processed': [],
             'pages_not_downloaded': set(),
             'images_not_downloaded': set()}
START_TIME = None

COLORS = {
    'GREEN': '\033[0;36m',  # 32
    'RED': '\033[0;31m',
    'YELLOW': '\033[0;33m',  # 32
    'BLUE': '\033[0;34m',  #
    'VIOLET': '\033[0;35m',  #
    'BOLD': '\033[1m',
    'NC': '\033[0m',
}
_COLOR_TO_CODE = {
    'g': COLORS['GREEN'],
    'r': COLORS['RED'],
    'y': COLORS['YELLOW'],
    'b': COLORS['BLUE'],
    'v': COLORS['VIOLET'],
    'bold': COLORS['BOLD']
}


def get_logger_name(module__name__, module___file__, package_name=None):
    if os.path.isabs(module___file__):
        # e.g. initcwd or editcfg
        module_name = os.path.splitext(os.path.basename(module___file__))[0]
        package_path = os.path.dirname(module___file__)
        package_name = os.path.basename(package_path)
        logger_name = "{}.{}".format(
            package_name,
            module_name)
    elif module__name__ == '__main__' or not module__name__.count('.'):
        # e.g. train_models.py or explore_data.py
        if package_name is None:
            package_name = os.path.basename(os.getcwd())
        logger_name = "{}.{}".format(
            package_name,
            os.path.splitext(module___file__)[0])
    elif module__name__.count('.') > 1:
        logger_name = '.'.join(module__name__.split('.')[-2:])
    else:
        # e.g. importing mlutils from train_models.py
        logger_name = module__name__
    return logger_name


def init_log(module__name__, module___file__=None, package_name=None):
    if module___file__:
        logger_ = logging.getLogger(get_logger_name(module__name__,
                                                    module___file__,
                                                    package_name))
    elif module__name__.count('.') > 1:
        logger_name = '.'.join(module__name__.split('.')[-2:])
        logger_ = logging.getLogger(logger_name)
    else:
        logger_ = logging.getLogger(module__name__)
    logger_.addHandler(NullHandler())
    return logger_


logger = init_log(__name__, __file__)


# ------
# Colors
# ------
def color(msg, msg_color='y', bold_msg=False):
    msg_color = msg_color.lower()
    colors = list(_COLOR_TO_CODE.keys())
    assert msg_color in colors, f'Wrong color: {msg_color}. Only these ' \
                                f'colors are supported: {msg_color}'
    if bold_msg:
        msg = f"{COLORS['BOLD']}{msg}{COLORS['NC']}"
    # e.g. bla bla \x1b[1mBOLD message\x1b[0m\x1b[0m bla bla
    msg = msg.replace(COLORS['NC'], COLORS['NC']+_COLOR_TO_CODE[msg_color])
    return f"{_COLOR_TO_CODE[msg_color]}{msg}{COLORS['NC']}"


def blue(msg):
    return color(msg, 'b')


def bold(msg):
    return color(msg, 'bold')


def green(msg):
    return color(msg, 'g')


def red(msg):
    return color(msg, 'r')


def violet(msg):
    return color(msg, 'v')


def yellow(msg):
    return color(msg)


def download_image(session, page_url, tag):
    global START_TIME, URLS_INFO
    src_image = tag[0].find('img')['src']
    if src_image.startswith('//'):
        logger.debug('Image found in the Wikipedia page')
        url_image = 'http:' + src_image
        req = get_response(session, url_image, HEADERS, HTTP_TIMEOUT)
        START_TIME = time.time()
        if req is not None:
            filename = urlparse(url_image).path.split('/')[-1].split(':')[-1]
            filepath = os.path.join(SAVE_DIRPATH, filename)
            with open(filepath, 'wb') as f:
                f.write(req.content)
            URLS_INFO['urls_status'][page_url].setdefault('status_image', f'Image downloaded and saved: {filepath}')
            msg = 'Image saved'
            print(green(f'{msg}!'))
            logger.debug(f'{msg}: {filepath}')
        else:
            logger.error('ConnectionError: request is None')
            print(yellow(f"Image couldn't be downloaded: {url_image}"))
            URLS_INFO['urls_status'][page_url].setdefault('status_image', f'ConnectionError: {url_image}')
            URLS_INFO['images_not_downloaded'].add(page_url)
    else:
        msg = f'Unsupported image found in the Wikipedia page: {src_image}'
        print(yellow(msg))
        logger.debug(msg)
        URLS_INFO['urls_status'][page_url].setdefault('status_image', f'Unsupported image found: {src_image}')
        URLS_INFO['images_not_downloaded'].add(page_url)


def download_page(session, page_url):
    try:
        global START_TIME, URLS_INFO
        req = get_response(session, page_url, HEADERS, HTTP_TIMEOUT)
        START_TIME = time.time()
        if req is None:
            logger.error('ConnectionError: request is None')
            URLS_INFO['urls_status'][page_url].setdefault('status_page', 'ConnectionError')
            URLS_INFO['pages_not_downloaded'].add(page_url)
            sleep()
            return None
        html = req.text
    except OSError as e:
        logger.exception(e)
        URLS_INFO['urls_status'][page_url].setdefault('status_page', 'OSError')
        URLS_INFO['pages_not_downloaded'].add(page_url)
        return None
    if req.status_code == 404:
        logger.error(f'404 - PAGE NOT FOUND: {page_url}')
        URLS_INFO['urls_status'][page_url].setdefault('status_page', '404 - PAGE NOT FOUND')
        URLS_INFO['pages_not_downloaded'].add(page_url)
    else:
        filename = urlparse(page_url).path.split('/')[-1] + '.html'
        filepath = os.path.join(SAVE_DIRPATH, filename)
        with open(filepath, 'w') as f:
            f.write(html)
        msg = 'Wikipedia page saved'
        print(green(f'{msg}!'))
        logger.debug(f'{msg}: {filepath}')
        URLS_INFO['urls_status'][page_url].setdefault('status_page', f'Page downloaded and saved: {filepath}')
    return req


def get_response(session, url, headers, timeout):
    global BYTES_DOWNLOADED
    try:
        req = session.get(url, headers=headers, timeout=timeout)
    except requests.exceptions.ConnectionError as e:
        logger.exception(e)
        return None
    if req.headers.get('content-length'):
        bytes_downloaded = int(req.headers['content-length'])
    else:
        logger.debug("No 'content-length' found in headers")
        logger.debug('Computing content length with len(req.content)')
        bytes_downloaded = len(req.content)
    BYTES_DOWNLOADED += bytes_downloaded
    return req


def setup_log():
    logger.setLevel(logging.DEBUG)
    # Create console handler and set level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create formatter
    formatters = {
        'console': 'format": "%(name)-{auto_field_width}s | %(levelname)-8s | %(message)s',
        'console_time': 'format": "%(asctime)s | %(levelname)-8s | %(message)s',
        'only_msg': '%(message)s',
        'simple': '%(levelname)-8s %(message)s',
        'verbose': '%(asctime)s | %(name)-{auto_field_width}s | %(levelname)-8s | %(message)s'
    }
    formatter = logging.Formatter(formatters['simple'])

    # Add formatter to ch
    ch.setFormatter(formatter)

    # Add ch to logger
    logger.addHandler(ch)


def sleep():
    global START_TIME
    assert START_TIME is not None
    sleep_time = DELAY_REQUESTS - (time.time() - START_TIME)
    if sleep_time > 0:
        rounded = round(sleep_time, 2)
        print(f'Sleeping for {rounded} second{"s" if rounded >= 2 else ""} ...')
        time.sleep(sleep_time)


def download_pages():
    global BYTES_DOWNLOADED, URLS_INFO, START_TIME
    filepath = os.path.join(MAIN_DIRPATH, LIST_PICKLE_FILENAME)
    req_session = requests.Session()
    logger.debug(f'Loading list of URLs: {filepath}')
    with open(filepath, 'rb') as f:
        list_physicists_urls = pickle.load(f)
    total_nb_urls = len(list_physicists_urls)
    logger.info(f'Number of URLs: {total_nb_urls}')
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
                logger.debug('No infobox-image found in the Wikipedia page')
                URLS_INFO['urls_status'][page_url].setdefault('status_image', 'No infobox-image found')
                logger.debug('Trying to find image in a `thumbinner` <div> class')
                a_tag = bs.select('.thumbinner > a')
                if a_tag:
                    download_image(req_session, page_url, a_tag)
                else:
                    logger.debug('No thumbinner-image found in the Wikipedia page')
                    print(yellow('No image found!'))
                    URLS_INFO['urls_status'][page_url]['status_image'] += '; No thumbinner-image found'
                    URLS_INFO['images_not_downloaded'].add(page_url)
        sleep()
        print()


def main():
    global BYTES_DOWNLOADED
    try:
        setup_log()
        download_pages()
    except KeyboardInterrupt:
        print(yellow('\nDownload stopped!'))
    except Exception as e:
        print(yellow('Download interrupted!'))
        # err_msg = "{}: {}".format(str(e.__class__).split("'")[1], e)
        # print(err_msg)
        logger.exception(e)
    # number of bytes in a mebibyte
    MBFACTOR = float(1 << 20)
    msg = blue('Total bytes downloaded:')
    print(f'{msg} {BYTES_DOWNLOADED} [{round(BYTES_DOWNLOADED/MBFACTOR, 2)} MiB]')


if __name__ == '__main__':
    main()
