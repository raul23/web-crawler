===========
Web scraper
===========
.. contents:: **Contents**
   :depth: 4
   :local:
   :backlinks: top

Exercises
=========
Get list of URLs to theoretical physicists' Wikipedia pages
-----------------------------------------------------------
.. code-block:: python

    import os
    import pickle
    import time
    from urllib.request import urlopen
    from bs4 import BeautifulSoup
   
    # Delay between HTTP requests (in seconds)
    delay_requests = 1
    list_physicists_urls = []
    domain = 'https://en.wikipedia.org/'
    bytes_downloaded = 0
    # Pages in category "Theoretical physicists"
    cat_page_url = 'https://en.wikipedia.org/w/index.php?title=Category:Theoretical_physicists'
    while True:
        more_cat_page = False
        html = urlopen(cat_page_url)
        bytes_downloaded += html.length
        start = time.time()
        bs = BeautifulSoup(html.read(), 'html.parser')
        # Select list of <a> tags containing relative URLs to theoretical physicists' Wikipedia pages
        phys_a_tags = bs.select('.mw-category-group > ul > li > a')
        # Extract the relative URLs and save them as absolute URLs
        for a_tag in phys_a_tags:
            if 'List of' not in a_tag.string:
                list_physicists_urls.append(domain + a_tag.get('href'))
        # Select the <a> tags containing relative URLs to the previous/next category pages
        page_a_tags = bs.select('#mw-pages > a')
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
            sleep_time = delay_requests - (now - start)
            print(f'Sleeping for {sleep_time} second')
            time.sleep(sleep_time)
        else:
            # No 'next' category page found. Thus, all necessary URLs have been extracted.
            print('No more category page found')
            break
    print(f"\n{len(list_physicists_urls)} URLs to theoretical physicists' Wikipedia pages found")
    # number of bytes in a megabyte
    MBFACTOR = float(1 << 20)
    print(f'Total bytes downloaded: {bytes_downloaded} [{round(bytes_downloaded/MBFACTOR, 2)} MB]')
