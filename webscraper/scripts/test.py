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

if False:
    # Save the list of URLs as a pickle file
    data = []
    filepath = os.path.expanduser('~/data/wikipedia/list_physicists_urls.pkl')
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)
    with open(filepath, 'rb') as f:
            data = pickle.load(f)
ipdb.set_trace()
