import logging
import os
import pickle
import time
from urllib.parse import unquote, urlparse

import requests
from bs4 import BeautifulSoup
import ipdb
logger = logging.getLogger('downloader')

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


def load_pickle(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
    except OSError:
        raise
    else:
        return data


def read_file(filepath, mode='r'):
    try:
        with open(filepath, mode) as f:
            return f.read()
    except OSError as e:
        raise


def setup_log():
    logger.setLevel(logging.DEBUG)
    # Create console handler and set level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # Create formatter
    formatters = {
        # 'console': '%(name)-{auto_field_width}s | %(levelname)-8s | %(message)s',
        'console_time': '%(asctime)s | %(levelname)-8s | %(message)s',
        'only_msg': '%(message)s',
        'simple': '%(levelname)-8s %(message)s',
        'verbose': '%(asctime)s | %(name)-{auto_field_width}s | %(levelname)-8s | %(message)s'
    }
    formatter = logging.Formatter(formatters['simple'])
    # Add formatter to ch
    ch.setFormatter(formatter)
    # Add ch to logger
    logger.addHandler(ch)


def write_file(filepath, data, overwrite=False, mode='w'):
    try:
        if os.path.isfile(filepath) and not overwrite:
            logger.debug(f'File already exists and overwrite is False: {filepath}')
        else:
            if os.path.isfile(filepath) and overwrite:
                logger.debug(f'File will be overwritten: {filepath}')
            with open(filepath, mode) as f:
                f.write(data)
            logger.debug("File written!")
    except OSError:
        raise


class Downloader:
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' \
                          '(KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 ' \
                          'RuxitSynthetic/1.0 v3029941779778713443 t1946166402082625254 ' \
                          'athf552e454 altpriv cvcv=2 smf=0'
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        self.headers = {'User-Agent': self.user_agent,
                        'Accept-Encoding': None,
                        'Content-Encoding': 'gzip'}
        self.http_timeout = 120
        self.session = requests.Session()
        self.delay_requests = 2
        self.main_dirpath = os.path.expanduser('~/data/wikipedia/')
        self.save_dirpath = os.path.join(self.main_dirpath, 'physicists')
        self.list_pickle_filepath = os.path.join(self.main_dirpath,
                                                 'list_physicists_urls.pkl')
        self.bytes_downloaded = 0
        self.urls_info = {'webpages_status': {},
                          'webpages_processed': [],
                          'webpages_from_cache': set(),
                          'webpages_not_downloaded': set(),
                          'images_from_cache': set(),
                          'images_not_downloaded': set()}

    def _download_image(self, page_url, tag, overwrite=False):
        src_image = tag.find('img')['src']
        ext = src_image.split('.')[-1]
        # Check if the image was already saved
        filename = self.get_saved_webpage_filename(page_url, with_ext=False)
        filepath = os.path.join(self.save_dirpath, filename + f'.{ext}')
        if os.path.isfile(filepath):
            logger.debug(f'The image was already saved: {filepath}')
            self.urls_info['webpages_status'][page_url].setdefault('status_image', 'Image already cached')
            self.urls_info['images_not_downloaded'].add(page_url)
            return
        else:
            logger.debug(f"The image wasn't found locally. Thus, an HTTP request will be sent to get the image.")
        if src_image.startswith('//'):
            logger.debug('Image found in the Wikipedia page')
            image_url = 'https:' + src_image
            response = self._get_response(image_url)
            if response is not None:
                if response.status_code == 200:
                    write_file(filepath, response.content, overwrite, mode='wb')
                    self.urls_info['webpages_status'][page_url].setdefault('status_image', f'Image saved: {filepath}')
                    msg = 'Image saved'
                    print(green(f'{msg}!'))
                    logger.debug(f'{msg}: {filepath}')
                elif response.status_code == 404:
                    logger.error(f'404 - IMAGE NOT FOUND: {image_url}')
                    self.urls_info['webpages_status'][page_url].setdefault('status_image',
                                                                           f'404 - IMAGE NOT FOUND: {image_url}')
                    self.urls_info['images_not_downloaded'].add(page_url)
                else:
                    logger.error(f"HTTP request returned with status code: {response.status_code}")
                    print(yellow(f"Image couldn't be retrieved: {page_url}"))
                    self.urls_info['webpages_status'][page_url].setdefault('status_image',
                                                                           f'HTTP status code: {response.status_code}')
            else:
                logger.error('ConnectionError: HTTP response is None')
                print(yellow(f"Image couldn't be downloaded: {image_url}"))
                self.urls_info['webpages_status'][page_url].setdefault('status_image', f'ConnectionError: {image_url}')
                self.urls_info['images_not_downloaded'].add(page_url)
        else:
            msg = f'Unsupported image found in the Wikipedia page: {src_image}'
            print(yellow(msg))
            logger.debug(msg)
            self.urls_info['webpages_status'][page_url].setdefault('status_image', f'Unsupported image found: {src_image}')
            self.urls_info['images_not_downloaded'].add(page_url)

    def _download_page(self, page_url, overwrite=False):
        # Check if the web page was already saved
        filename = self.get_saved_webpage_filename(page_url)
        filepath = os.path.join(self.save_dirpath, filename)
        if os.path.isfile(filepath):
            logger.debug(f'The web page was already saved: {filepath}')
            logger.debug('Reading the web page from local disk ...')
            self.urls_info['webpages_status'][page_url].setdefault('status_page', f'Web page already cached: {filepath}')
            self.urls_info['webpages_from_cache'].add(page_url)
            text = read_file(filepath)
            return 123, text
        else:
            logger.debug(f"The web page wasn't found locally. Thus, an HTTP request will be sent to get the web page.")
        try:
            response = self._get_response(page_url)
            if response is None:
                logger.error('ConnectionError: HTTP response is None')
                print(red("Couldn't download the page!"))
                self.urls_info['webpages_status'][page_url].setdefault('status_page', 'ConnectionError')
                self.urls_info['webpages_not_downloaded'].add(page_url)
                self._sleep()
                return None
            html = response.text
        except OSError as e:
            logger.exception(e)
            self.urls_info['webpages_status'][page_url].setdefault('status_page', 'OSError')
            self.urls_info['webpages_not_downloaded'].add(page_url)
            return None
        if response.status_code == 200:
            write_file(filepath, html, overwrite)
            msg = 'Web page saved'
            print(green(f'{msg}!'))
            logger.debug(f'{msg}: {filepath}')
            self.urls_info['webpages_status'][page_url].setdefault('status_page', f'Web page saved: {filepath}')
        elif response.status_code == 404:
            logger.error(f'404 - PAGE NOT FOUND: {page_url}')
            print(red(f"Couldn't download the page: {page_url}"))
            self.urls_info['webpages_status'][page_url].setdefault('status_page', '404 - PAGE NOT FOUND')
            self.urls_info['webpages_not_downloaded'].add(page_url)
        else:
            logger.error(f"HTTP request returned with status code: {response.status_code}")
            print(red(f"Couldn't download the webpage: {page_url}"))
            self.urls_info['webpages_status'][page_url].setdefault('status_page',
                                                                   f'HTTP status code: {response.status_code}')
            self.urls_info['webpages_not_downloaded'].add(page_url)
        return response

    def _get_response(self, url):
        try:
            response = self.session.get(url, headers=self.headers, timeout=self.http_timeout)
            self._sleep()
        except requests.exceptions.ConnectionError as e:
            logger.exception(e)
            self._sleep()
            return None
        if response.headers.get('content-length'):
            bytes_downloaded = int(response.headers['content-length'])
        elif response:
            logger.debug("No 'content-length' found in headers")
            logger.debug('Computing content length with len(req.content)')
            bytes_downloaded = len(response.content)
        else:
            # TODO: get traceback() to retrieve error
            logger.error('request object is None')
            return None
        self.bytes_downloaded += bytes_downloaded
        return response

    def _sleep(self):
        print(f'Sleeping for {self.delay_requests} second{"s" if self.delay_requests >= 2 else ""} ...')
        time.sleep(self.delay_requests)

    def download_pages(self):
        def extract_retvals(retvals):
            if retvals:
                status_code, text = retvals[0], retvals[1]
            else:
                status_code, text = None, None
            return status_code, text

        logger.debug(f'Loading list of URLs: {self.list_pickle_filepath}')
        list_physicists_urls = load_pickle(self.list_pickle_filepath)
        total_nb_urls = len(list_physicists_urls)
        logger.info(f'Number of URLs: {total_nb_urls}')
        print()
        for i, page_url in enumerate(list_physicists_urls):
            page_url = unquote(page_url)
            print(violet(f'processing url {i+1} of {total_nb_urls}: ') + page_url)
            logger.debug(f'processing url {i+1}: {page_url}')
            self.urls_info['webpages_status'].setdefault(page_url, {})
            self.urls_info['webpages_processed'].append(page_url)
            retvals = self._download_page(page_url)
            status_code, text = extract_retvals(retvals)
            if status_code in [200, 123]:
                # Get physicist's image and save it separately
                bs = BeautifulSoup(text, 'html.parser')
                td_tag = bs.select('.infobox-image')
                if td_tag:
                    if len(td_tag) > 1:
                        logger.warning(f'Unexpected: there are more than one infobox-image: {page_url}')
                    td_tag = td_tag[0]
                    self._download_image(page_url, td_tag)
                else:
                    logger.debug('No infobox-image found in the Wikipedia page')
                    self.urls_info['webpages_status'][page_url].setdefault('status_image', 'No infobox-image found')
                    logger.debug('Trying to find image in a `thumbinner` <div> class')
                    a_tag = bs.select('.thumbinner > a')
                    # TODO: make sure it is only one <div> tag
                    if a_tag:
                        if len(td_tag) > 1:
                            logger.debug(f'There are {len(td_tag)} thumbinner images: {page_url}')
                        a_tag = a_tag[0]
                        self._download_image(page_url, a_tag)
                    else:
                        logger.debug('No thumbinner-image found in the Wikipedia page')
                        print(yellow('No image found!'))
                        self.urls_info['webpages_status'][page_url]['status_image'] += '; No thumbinner-image found'
                        self.urls_info['images_not_downloaded'].add(page_url)
            else:
                print(yellow(f'Status code when requesting the Wikipedia page: {req.status_code}'))
                print(yellow("No Wikipedia page found!"))
                logger.debug("Since the Wikipedia page wasn't found, no image could be retrieved")
            print()

    @staticmethod
    def get_saved_webpage_filename(page_url, with_ext=True):
        last_part = urlparse(page_url).path.split('/')[-1]
        if last_part:
            filename = last_part
        else:
            filename = urlparse(page_url).path.split('/')[-2]
        if with_ext:
            filename += '.html'
        return filename


def main():
    exit_code = 0
    try:
        setup_log()
        downloader = Downloader()
        downloader.download_pages()
    except KeyboardInterrupt:
        print(yellow('\nDownload stopped!'))
        exit_code = 2
    except Exception as e:
        print(yellow('Download interrupted!'))
        logger.exception(e)
        exit_code = 1
    # Number of bytes in a mebibyte
    MBFACTOR = float(1 << 20)
    msg = blue('Total bytes downloaded:')
    bytes_downloaded = downloader.bytes_downloaded
    print(f'{msg} {bytes_downloaded} [{round(bytes_downloaded/MBFACTOR, 2)} MiB]')
    return exit_code


if __name__ == '__main__':
    retcode = main()
    msg = f'Program exited with {retcode}'
    if retcode == 1:
        logger.error(msg)
    else:
        logger.info(msg)
