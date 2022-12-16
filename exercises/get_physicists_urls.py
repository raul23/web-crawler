import argparse
import os
import pickle
import time
import sys
from urllib.request import urlopen
from bs4 import BeautifulSoup


def setup_argparser():
    msg = 'Get URLs to Wikipedia pages of theoretical physicists'
    name_output = 'pickle_file'
    parser = argparse.ArgumentParser(
        description='',
        usage=f"python %(prog)s [OPTIONS] {{{name_output}}}\n\n{msg}",
        # ArgumentDefaultsHelpFormatter
        # HelpFormatter
        # RawDescriptionHelpFormatter
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--delay-requests', metavar='DELAY', dest='delay_requests',
                        default=2, type=int, help='Delay in seconds between HTTP requests.')
    parser.add_argument(
        name_output, default=None, nargs=1,
        help="Path to the pickle file that will contain the list of URLs to theoretical physicists' Wikipedia pages.")
    return parser


if __name__ == '__main__':
    list_physicists_urls = []
    domain = 'https://en.wikipedia.org'
    bytes_downloaded = 0
    parser = setup_argparser()
    args = parser.parse_args()
    args.pickle_file = args.pickle_file[0]
    # Pages in category "Theoretical physicists"
    cat_page_url = 'https://en.wikipedia.org/w/index.php?title=Category:Theoretical_physicists'
    page_num = 1
    dirpath = os.path.dirname(args.pickle_file)
    if not os.path.isdir(dirpath):
        print(f"The directory doesn't exist: {dirpath}")
        sys.exit(1)
    while True:
        more_cat_page = False
        html = urlopen(cat_page_url)
        content = html.read()
        if html.length is None:
            bytes_downloaded += len(content)
        else:
            bytes_downloaded += html.length
        print(f'Processing category page {page_num}')
        page_num += 1
        start = time.time()
        bs = BeautifulSoup(content, 'html.parser')
        # Select list of <a> tags containing relative URLs to theoretical physicists' Wikipedia pages
        phys_a_tags = bs.select('.mw-category-group > ul > li > a')
        # Extract the relative URLs and save them as absolute URLs
        nb_urls_found = 0
        for a_tag in phys_a_tags:
            if 'List of' not in a_tag.string:
                list_physicists_urls.append(domain + a_tag.get('href'))
                nb_urls_found += 1
        print(f'Found {nb_urls_found} URLs')
        # Select the <a> tags containing relative URLs to the previous/next category pages
        page_a_tags = bs.select('#mw-pages > a')
        print()
        for page_a_tag in page_a_tags:
            # Determine if there is more 'next' category page to process
            if 'next page' in page_a_tag.string:
                if page_a_tag.get('href'):
                    cat_page_url = domain + page_a_tag.get('href')
                    more_cat_page = True
                    print('Another category page found')
                break
        # If a 'next' category page was found to be processed
        if more_cat_page:
            now = time.time()
            sleep_time = args.delay_requests - (now - start)
            print(f'Sleeping for {round(sleep_time, 3)} second')
            time.sleep(sleep_time)
        else:
            # No 'next' category page found. Thus, all necessary URLs have been extracted.
            print('No more category page found')
            break

    print(f"\n{len(list_physicists_urls)} URLs found")
    # number of bytes in a mebibyte
    MBFACTOR = float(1 << 20)
    print(f'Total bytes downloaded: {bytes_downloaded} [{round(bytes_downloaded/MBFACTOR, 2)} MiB]')
    # Save the list of URLs as a pickle file
    filepath = os.path.expanduser(args.pickle_file)
    print(f'Saving list of URLs: {filepath}')
    with open(filepath, 'wb') as f:
        pickle.dump(list_physicists_urls, f)
    sys.exit(0)
