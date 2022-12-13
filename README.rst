=====================
Web crawler + scraper
=====================
.. contents:: **Contents**
   :depth: 4
   :local:
   :backlinks: top

Exercises
---------
1. Get list of URLs of theoretical physicists' Wikipedia pages
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Starting from `Category:Theoretical physicists <https://en.wikipedia.org/w/index.php?title=Category:Theoretical_physicists>`_, get all the absolute URLs of theoretical physicists' Wikipedia pages by processing the list of relative URLs in the section **Pages in category "Theoretical physicists"** and crawling through the next pages until no more *next page* found.

.. code-block:: python

   import time
   from urllib.request import urlopen
   from bs4 import BeautifulSoup

   # Delay between HTTP requests (in seconds)
   DELAY_REQUESTS = 1
   list_physicists_urls = []
   domain = 'https://en.wikipedia.org'
   bytes_downloaded = 0
   # Pages in category "Theoretical physicists"
   cat_page_url = 'https://en.wikipedia.org/w/index.php?title=Category:Theoretical_physicists'
   page_num = 1
   while True:
       more_cat_page = False
       html = urlopen(cat_page_url)
       bytes_downloaded += html.length
       print(f'Processing category page {page_num}')
       page_num += 1
       start = time.time()
       bs = BeautifulSoup(html.read(), 'html.parser')
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
           sleep_time = DELAY_REQUESTS - (now - start)
           print(f'Sleeping for {round(sleep_time, 3)} second')
           time.sleep(sleep_time)
       else:
           # No 'next' category page found. Thus, all necessary URLs have been extracted.
           print('No more category page found')
           break

   print(f"\n{len(list_physicists_urls)} URLs found")
   # Number of bytes in a mebibyte
   # ref.: https://stackoverflow.com/a/40957594
   MBFACTOR = float(1 << 20)
   print(f'Total bytes downloaded: {bytes_downloaded} [{round(bytes_downloaded/MBFACTOR, 2)} MiB]')

Showing the first 4 URLs in the list::

   ipdb> list_physicists_urls[:4]
   
   ['https://en.wikipedia.org//wiki/Alexei_Abrikosov_(physicist)', 'https://en.wikipedia.org//wiki/Vadym_Adamyan', 'https://en.wikipedia.org//wiki/David_Adler_(physicist)', 'https://en.wikipedia.org//wiki/Diederik_Aerts']

`:information_source:`

  - The Python script can be found at `get_physicists_urls.py <https://github.com/raul23/web-crawler/blob/main/exercises/get_physicists_urls.py>`_
  - The Python script requires the ``BeautifulSoup`` library which can be installed with:
  
    ``pip install pip install beautifulsoup4``
  - The Python script saves the list of URLs as a pickle file if given the 's' option when running the script: 
  
    ``python get_physicists_urls.py s``

2. Download Wikipedia pages
'''''''''''''''''''''''''''
From the `previous list <#get-list-of-urls-of-theoretical-physicists-wikipedia-pages>`_ of URLs to Wikipedia pages, download each page (html only) along with the image in the info box if it is found.

`:information_source:`

  - The Python script can be found at `get_physicists_urls.py <https://github.com/raul23/web-crawler/blob/main/exercises/get_physicists_urls.py>`_ 
  - The Python script requires the ``BeautifulSoup`` and ``requests`` libraries which can be installed with:
  
    - ``pip install beautifulsoup4``
    - ``pip install requests``
  - By default, there is a delay of 2 seconds between HTTP requests.

Here are the general steps for downloading the Wikipedia pages with the corresponding images:

1. Load the pickle file containing the list of URLs which was generated from the `previous exercise <#get-list-of-urls-of-theoretical-physicists-wikipedia-pages>`_
2. For each URL, 

   1. download the associated Wikipedia page (html only) with the ``requests`` package
   2. download the corresponding image if it is found in the info box (i.e. in a ``<td>`` tag with the ``infobox-image`` class): e.g. `Alexei Abrikosov <https://en.wikipedia.org/wiki/Alexei_Abrikosov_(physicist)>`_
   3. if no image is found in the info-box, then try to get it as a thumb picture (i.e. in a ``<div>`` tag with the ``thumbinner`` class): e.g. `Oriol Bohigas Martí <https://en.wikipedia.org/wiki/Oriol_Bohigas_Mart%C3%AD>`_ 
3. Every Wikipedia page (html) and its corresponing image are saved locally within a directory as specified by the user
4. Useful information for the casual user is printed in the console (important messages are colored, e.g. warning that an image couldn't be downloaded) and the logger hides the rest of the information useful for debugging

.. https://archive.vn/mu9PH
.. https://archive.vn/Na9fK

.. raw:: html

   <p align="center"><img src="./images/ex2_output.png"></p>
   <p align="center"><img src="./images/wikipedia_directory.png"></p>

3. Extract DOB and DOD from Wikipedia pages [TODO]
''''''''''''''''''''''''''''''''''''''''''''''''''
`:information_source:`

  - **DOB:** *Date of Birth*
  - **DOD:** *Date of Death*

`:warning:` TODO

4. Extract more information from the information box [TODO]
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Apart from the *DOB* and *DOD*, there are more information that can be extracted from the information box associated with physicists such as:

- Place of birth and death
- Citizenship
- Alma mater
- Known for
- Awards
- Fields
- Institutions
- Thesis
- Doctoral advisor
- Other academic advisors
- Doctoral students
- Other notable students
- Influences
- Influenced

See for example: `Wolfgang Pauli <https://en.wikipedia.org/wiki/Wolfgang_Pauli>`_

Some of these information can also be gleaned from other parts of the document.

`:warning:` TODO
