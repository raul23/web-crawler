import os
import pickle
from urllib.parse import urlparse
# Third-party modules/libraries
from pywebcopy import save_webpage

list_physicists_urls = []
filepath = os.path.expanduser('~/data/wikipedia/list_physicists_urls.pkl')
print(f'Loading list of URLs: {filepath}')
with open(filepath, 'rb') as f:
    list_physicists_urls = pickle.load(f)
print(f'Number of URLs: {len(list_physicists_urls)}')
import ipdb
ipdb.set_trace()
for url in list_physicists_urls:
    filename = urlparse(url).path.split('/')[-1]
    save_webpage(
        url='https://en.wikipedia.org/wiki/Alexei_Abrikosov_(physicist)',
        project_folder=os.path.expanduser(f'~/data/wikipedia/theoretical_physicists_pages'),
        bypass_robots=True,
        debug=False,
        open_in_browser=False,
        delay=None,
        threaded=False
    )
    ipdb.set_trace()
