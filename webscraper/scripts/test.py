import os
import pickle
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
import ipdb
# ipdb.set_trace()

if False:
    html = urlopen('https://en.wikipedia.org/wiki/Erwin_Schr%C3%B6dinger')
    bs = BeautifulSoup(html.read(), 'html.parser')
    div_catlinks = bs.find('div', {'id': 'mw-normal-catlinks'})
    catlinks = div_catlinks.find_all('li')
    found_atheists = []
    for catlink in catlinks:
        if 'atheist' in catlink.get_text():
            found_atheists.append(catlink)

if True:
    delay_requests = 1
    list_physicists_urls = []
    # Pages in category "Theoretical physicists"
    cat_page_url = 'https://en.wikipedia.org/w/index.php?title=Category:Theoretical_physicists'
    while True:
        more_cat_page = False
        html = urlopen(cat_page_url)
        start = time.time()
        bs = BeautifulSoup(html.read(), 'html.parser')
        phys_a_tags = bs.select('.mw-category-group > ul > li > a')
        for a_tag in phys_a_tags:
            if 'List of' not in a_tag.string:
                list_physicists_urls.append('https://en.wikipedia.org/' + a_tag.get('href'))
        page_a_tags = bs.select('#mw-pages > a')
        for page_a_tag in page_a_tags:
            if 'next page' in page_a_tag.string:
                if page_a_tag.get('href'):
                    cat_page_url = 'https://en.wikipedia.org/' + page_a_tag.get('href')
                    more_cat_page = True
                    print('Another page category found')
                break
        if more_cat_page:
            now = time.time()
            sleep_time = delay_requests - (now - start)
            print(f'Sleeping for {sleep_time} second')
            time.sleep(sleep_time)
        else:
            print('No more page category found')
            break
    print(f'{len(list_physicists_urls)} physicists found')
    filepath = os.path.expanduser('~/data/wikipedia/list_physicists_urls.pkl')
    with open(filepath, 'wb') as f:
        pickle.dump(list_physicists_urls, f)
    with open(filepath, 'rb') as f:
            data = pickle.load(f)
ipdb.set_trace()