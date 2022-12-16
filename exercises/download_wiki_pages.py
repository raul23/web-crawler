#!/usr/bin/env python
import argparse
import logging
import os
import pickle
import time
from argparse import Namespace
from types import SimpleNamespace
from urllib.parse import unquote, urlparse

import requests
from bs4 import BeautifulSoup
import ipdb
logger = logging.getLogger('downloader')
__version__ = '0.1'
QUIET = False


class Downloader:
    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' \
                 '(KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 ' \
                 'RuxitSynthetic/1.0 v3029941779778713443 t1946166402082625254 ' \
                 'athf552e454 altpriv cvcv=2 smf=0'
    HTTP_TIMEOUT = 120
    DELAY_REQUESTS = 2

    def __init__(self):
        self.user_agent = Downloader.USER_AGENT
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        self.headers = {'User-Agent': self.user_agent,
                        'Accept-Encoding': None,
                        'Content-Encoding': 'gzip'}
        self.http_timeout = Downloader.HTTP_TIMEOUT
        self.session = requests.Session()
        self.delay_requests = Downloader.DELAY_REQUESTS
        self.output_directory = None
        self.input_pickle_file = None
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
        filepath = os.path.join(self.output_directory, filename + f'.{ext}')
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
                    print_(green(f'{msg}!'))
                    logger.debug(f'{msg}: {filepath}')
                elif response.status_code == 404:
                    logger.error(f'404 - IMAGE NOT FOUND: {image_url}')
                    self.urls_info['webpages_status'][page_url].setdefault('status_image',
                                                                           f'404 - IMAGE NOT FOUND: {image_url}')
                    self.urls_info['images_not_downloaded'].add(page_url)
                else:
                    logger.error(f"HTTP request returned with status code: {response.status_code}")
                    print_(yellow(f"Image couldn't be retrieved: {page_url}"))
                    self.urls_info['webpages_status'][page_url].setdefault('status_image',
                                                                           f'HTTP status code: {response.status_code}')
            else:
                logger.error('ConnectionError: HTTP response is None')
                print_(yellow(f"Image couldn't be downloaded: {image_url}"))
                self.urls_info['webpages_status'][page_url].setdefault('status_image', f'ConnectionError: {image_url}')
                self.urls_info['images_not_downloaded'].add(page_url)
        else:
            msg = f'Unsupported image found in the Wikipedia page: {src_image}'
            print_(yellow(msg))
            logger.debug(msg)
            self.urls_info['webpages_status'][page_url].setdefault('status_image', f'Unsupported image found: {src_image}')
            self.urls_info['images_not_downloaded'].add(page_url)

    def _download_page(self, page_url, overwrite=False):
        # Check if the web page was already saved
        filename = self.get_saved_webpage_filename(page_url)
        filepath = os.path.join(self.output_directory, filename)
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
                print_(red("Couldn't download the page!"))
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
            print_(green(f'{msg}!'))
            logger.debug(f'{msg}: {filepath}')
            self.urls_info['webpages_status'][page_url].setdefault('status_page', f'Web page saved: {filepath}')
        elif response.status_code == 404:
            logger.error(f'404 - PAGE NOT FOUND: {page_url}')
            print_(red(f"Couldn't download the page: {page_url}"))
            self.urls_info['webpages_status'][page_url].setdefault('status_page', '404 - PAGE NOT FOUND')
            self.urls_info['webpages_not_downloaded'].add(page_url)
        else:
            logger.error(f"HTTP request returned with status code: {response.status_code}")
            print_(red(f"Couldn't download the webpage: {page_url}"))
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
        print_(f'Sleeping for {self.delay_requests} second{"s" if self.delay_requests >= 2 else ""} ...')
        time.sleep(self.delay_requests)

    def download_pages(self, **kwargs):
        def extract_retvals(retvals):
            if retvals:
                status_code, text = retvals[0], retvals[1]
            else:
                status_code, text = None, None
            return status_code, text

        self.__dict__.update(kwargs)
        logger.debug(f'Loading list of URLs: {self.input_pickle_file}')
        list_physicists_urls = load_pickle(self.input_pickle_file)
        total_nb_urls = len(list_physicists_urls)
        logger.info(f'Number of URLs: {total_nb_urls}')
        print_('')
        for i, page_url in enumerate(list_physicists_urls):
            page_url = unquote(page_url)
            print_(violet(f'processing url {i+1} of {total_nb_urls}: ') + page_url)
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
                        print_(yellow('No image found!'))
                        self.urls_info['webpages_status'][page_url]['status_image'] += '; No thumbinner-image found'
                        self.urls_info['images_not_downloaded'].add(page_url)
            else:
                print_(yellow(f'Status code when requesting the Wikipedia page: {req.status_code}'))
                print_(yellow("No Wikipedia page found!"))
                logger.debug("Since the Wikipedia page wasn't found, no image could be retrieved")
            print_('')

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


class ArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        # self.print_help(sys.stderr)
        # self.print_usage(sys.stderr)
        print_(self.format_usage().splitlines()[0])
        self.exit(2, color(f'\nerror: {message}\n', 'r'))


# Ref.: https://stackoverflow.com/a/32891625/14664104
class MyFormatter(argparse.HelpFormatter):
    """
    Corrected _max_action_length for the indenting of subactions
    """

    def add_argument(self, action):
        if action.help is not argparse.SUPPRESS:

            # find all invocations
            get_invocation = self._format_action_invocation
            invocations = [get_invocation(action)]
            current_indent = self._current_indent
            for subaction in self._iter_indented_subactions(action):
                # compensate for the indent that will be added
                indent_chg = self._current_indent - current_indent
                added_indent = 'x' * indent_chg
                invocations.append(added_indent + get_invocation(subaction))
            # print_('inv', invocations)

            # update the maximum item length
            invocation_length = max([len(s) for s in invocations])
            action_length = invocation_length + self._current_indent
            self._action_max_length = max(self._action_max_length,
                                          action_length)

            # add the item to the list
            self._add_item(self._format_action, [action])

    # Ref.: https://stackoverflow.com/a/23941599/14664104
    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []
            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)

            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            # change to
            #    -s, --long ARGS
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    # parts.append('%s %s' % (option_string, args_string))
                    parts.append('%s' % option_string)
                parts[-1] += ' %s'%args_string
            return ', '.join(parts)


# ------
# Colors
# ------
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


def color(msg, msg_color='y', bold_msg=False):
    msg_color = msg_color.lower()
    colors = list(_COLOR_TO_CODE.keys())
    assert msg_color in colors, f'Wrong color: {msg_color}. Only these ' \
                                f'colors are supported: {msg_color}'
    msg = bold(msg) if bold_msg else msg
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


# ---------
# Utilities
# ---------
_DEFAULT_MSG = ' (default: {})'
_LOGGING_FORMATTER = 'simple'
_LOGGING_LEVEL = 'info'


class OptionsChecker:
    def __init__(self, add_opts, remove_opts):
        self.add_opts = init_list(add_opts)
        self.remove_opts = init_list(remove_opts)

    def check(self, opt_name):
        return not self.remove_opts.count(opt_name) or \
               self.add_opts.count(opt_name)


# TODO: important, mention options are grouped in each function
# TODO: important, mention add_opts supersede remove_opts
# General options
def add_general_options(parser, add_opts=None, remove_opts=None,
                        program_version=__version__,
                        title='General options'):
    checker = OptionsChecker(add_opts, remove_opts)
    parser_general_group = parser.add_argument_group(title=title)
    if checker.check('help'):
        parser_general_group.add_argument('-h', '--help', action='help',
                                          help='Show this help message and exit.')
    # TODO: package name too? instead of program name
    if checker.check('version'):
        parser_general_group.add_argument(
            '-v', '--version', action='version',
            version=f'%(prog)s v{program_version}',
            help="Show program's version number and exit.")
    if checker.check('quiet'):
        parser_general_group.add_argument(
            '-q', '--quiet', action='store_true',
            help='Enable quiet mode, i.e. nothing will be printed.')
    if checker.check('verbose'):
        # TODO: important test traceback
        parser_general_group.add_argument(
            '--verbose', action='store_true',
            help='Print various debugging information, e.g. print traceback '
                 'when there is an exception.')
    # TODO: important, add color to default values (other places too)
    if checker.check('log-level'):
        parser_general_group.add_argument(
            '--log-level', dest='logging_level',
            choices=['debug', 'info', 'warning', 'error'], default=_LOGGING_LEVEL,
            help='Set logging level.' + get_default_message(_LOGGING_LEVEL))
    if checker.check('log-format'):
        # TODO: explain each format
        parser_general_group.add_argument(
            '--log-format', dest='logging_formatter',
            choices=['console', 'only_msg', 'simple',], default=_LOGGING_FORMATTER,
            help='Set logging formatter.' + get_default_message(_LOGGING_FORMATTER))
    return parser_general_group


def get_default_message(default_value):
    return green(f' (default: {default_value})')


def init_list(list_):
    return [] if list_ is None else list_


def load_pickle(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
    except OSError:
        raise
    else:
        return data


def namespace_to_dict(ns):
    namspace_classes = [Namespace, SimpleNamespace]
    # TODO: check why not working anymore
    # if isinstance(ns, SimpleNamespace):
    if type(ns) in namspace_classes:
        adict = vars(ns)
    else:
        adict = ns
    for k, v in adict.items():
        # if isinstance(v, SimpleNamespace):
        if type(v) in namspace_classes:
            v = vars(v)
            adict[k] = v
        if isinstance(v, dict):
            namespace_to_dict(v)
    return adict


def print_(msg):
    global QUIET
    if not QUIET:
        print(msg)


def read_file(filepath, mode='r'):
    try:
        with open(filepath, mode) as f:
            return f.read()
    except OSError as e:
        raise


# Ref.: https://stackoverflow.com/a/4195302/14664104
def required_length(nmin, nmax):
    class RequiredLength(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if not nmin <= len(values) <= nmax:
                if nmin == nmax:
                    msg = 'argument "{f}" requires {nmin} arguments'.format(
                        f=self.dest, nmin=nmin, nmax=nmax)
                else:
                    msg = 'argument "{f}" requires between {nmin} and {nmax} ' \
                          'arguments'.format(f=self.dest, nmin=nmin, nmax=nmax)
                raise argparse.ArgumentTypeError(msg)
            setattr(args, self.dest, values)
    return RequiredLength


def setup_log(quiet=False, verbose=False, logging_level=_LOGGING_LEVEL,
              logging_formatter=_LOGGING_FORMATTER):
    if not quiet:
        if verbose:
            logger.setLevel('DEBUG')
        else:
            logging_level = logging_level.upper()
            logger.setLevel(logging_level)
        # Create console handler and set level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # Create formatter
        if logging_formatter:
            formatters = {
                # 'console': '%(name)-{auto_field_width}s | %(levelname)-8s | %(message)s',
                'console': '%(asctime)s | %(levelname)-8s | %(message)s',
                'only_msg': '%(message)s',
                'simple': '%(levelname)-8s %(message)s',
                'verbose': '%(asctime)s | %(name)-{auto_field_width}s | %(levelname)-8s | %(message)s'
            }
            formatter = logging.Formatter(formatters[logging_formatter])
            # Add formatter to ch
            ch.setFormatter(formatter)
        # Add ch to logger
        logger.addHandler(ch)
        # =============
        # Start logging
        # =============
        logger.info("Running {} v{}".format(__file__, __version__))
        logger.info("Verbose option {}".format("enabled" if verbose else "disabled"))


def setup_argparser():
    width = os.get_terminal_size().columns - 5
    # Setup the parser
    name_input = 'input_pickle_file'
    name_output = 'output_directory'
    msg = 'Download Wikipedia pages of theoretical physicists.'
    parser = ArgumentParser(
        description=f"{COLORS['RED']}IMPORTANT{COLORS['NC']}: if an argument has spaces, enclose it within quotation "
                    "marks, e.g. -u 'Mozilla/5.0 (11; Linux x86_64) AppleWebKit/537.36'",
        usage=f"{COLORS['BLUE']}python %(prog)s [OPTIONS] {{{name_input}}} {{{name_output}}}{COLORS['NC']}\n\n{msg}",
        add_help=False,
        # ArgumentDefaultsHelpFormatter
        # HelpFormatter
        # RawDescriptionHelpFormatter
        formatter_class=lambda prog: MyFormatter(
            prog, max_help_position=50, width=width))
    general_group = add_general_options(
        parser,
        remove_opts=[],
        program_version=__version__,
        title=yellow('General options'))
    # ====================
    # HTTP requests config
    # ====================
    http_req_group = parser.add_argument_group(title=yellow('HTTP requests options'))
    http_req_group.add_argument(
        '-u', '--user-agent', metavar='USER_AGENT', dest='user_agent',
        default=Downloader.USER_AGENT,
        help='User Agent.' + get_default_message(Downloader.USER_AGENT))
    http_req_group.add_argument(
        '-t', '--http-timeout', metavar='TIMEOUT', dest='http_timeout',
        default=Downloader.HTTP_TIMEOUT, type=int,
        help='HTTP timeout in seconds.' + get_default_message(Downloader.HTTP_TIMEOUT))
    http_req_group.add_argument(
        '-d', '--delay-requests', metavar='DELAY', dest='delay_requests',
        default=Downloader.DELAY_REQUESTS, type=int,
        help='Delay in seconds between HTTP requests.' + get_default_message(Downloader.DELAY_REQUESTS))
    # ==============
    # Input argument
    # ==============
    input_group = parser.add_argument_group(title=yellow('Input argument'))
    input_group.add_argument(
        name_input, default=None, nargs=1,
        help="Path to the pickle file containing the list of URLs to theoretical physicists' Wikipedia pages.")
    # ==============
    # Output argument
    # ==============
    output_group = parser.add_argument_group(title=yellow('Output argument'))
    output_group.add_argument(
        name_output, default=None, nargs=1,
        help="Path to the directory where the Wikipedia pages and corresponding images will be saved.")
    return parser


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


def main():
    global QUIET
    downloader = None
    exit_code = 0
    try:
        parser = setup_argparser()
        args = parser.parse_args()
        args.input_pickle_file = args.input_pickle_file[0]
        args.output_directory = args.output_directory[0]
        QUIET = args.quiet
        setup_log(args.quiet, args.verbose, args.logging_level, args.logging_formatter)
        downloader = Downloader()
        downloader.download_pages(**namespace_to_dict(args))
    except KeyboardInterrupt:
        print_(yellow('\nDownload stopped!'))
        exit_code = 2
    except Exception as e:
        print_(yellow('Download interrupted!'))
        logger.exception(e)
        exit_code = 1
    bytes_downloaded = downloader.bytes_downloaded if downloader else 0
    # Number of bytes in a mebibyte
    MBFACTOR = float(1 << 20)
    msg = blue('Total bytes downloaded:')
    print_(f'{msg} {bytes_downloaded} [{round(bytes_downloaded/MBFACTOR, 2)} MiB]')
    return exit_code


if __name__ == '__main__':
    retcode = main()
    msg = f'Program exited with {retcode}'
    if retcode == 1:
        logger.error(msg)
    else:
        logger.info(msg)
