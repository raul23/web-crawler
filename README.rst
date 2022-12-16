=====================
Web crawler + scraper
=====================
.. contents:: **Contents**
   :depth: 4
   :local:
   :backlinks: top

Scripts
=======
``download_wiki_pages.py``: download Wikipedia pages of theoretical physicists
------------------------------------------------------------------------------
This script is from `Exercise 2 <#download-wikipedia-pages>`_. It takes as input a pickle file containing URLs to Wikipedia pages of theoretical physicists (see `Exercise 1 <#get-list-of-urls-of-theoretical-physicists-wikipedia-pages>`_).

Dependencies
''''''''''''
This is the environment on which the script was tested:

* **Platforms:** macOS
* **Python**: versions **3.7** and **3.8**
* `requests <https://requests.readthedocs.io/en/latest/>`_: **v2.28.1**, for sending HTTP GET requests
* `beautifulsoup4 <https://www.crummy.com/software/BeautifulSoup/>`_ **v4.11.1**, for screen-scraping

Usage
'''''
Run the script
```````````````
Run the script by specifying the paths to the `pickle file <#download-wikipedia-pages>`_ and the ouput directory where the downloaded Wikipedia pages will be saved::

   $ pyton download_wiki_pages.py ~/Data/wikipedia/list_physicists_urls.pkl ~/Data/wikipedia/physicists/ --log-format only_msg --log-level debug
   
`:information_source:`

  - ``~/Data/wikipedia/list_physicists_urls.pkl``: pickle file containing list of URLs to Wikipedia 
    pages of theoretical physicists
  - ``~/Data/wikipedia/physicists/``: ouput directory where the downloaded Wikipedia pages will be saved
  - ``--log-format only_msg``: display only the logging message without the timestamp or the logging level
  - ``--log-level debug``: display all logging messages with the ``debug`` logging level
   
  Check `List of options <#list-of-options>`_ to know more about the other options you can use.
   
`:star:`

   In order to stop the ``start_dv`` script at any moment, press
   ``ctrl`` + ``c``.

List of options
```````````````
To display the script's list of options and their descriptions, use the ``-h`` option::

   $ pyton download_wiki_pages.py -h

   usage: python download_wiki_pages.py [OPTIONS] {input_pickle_file} {output_directory}

General options:

-h, --help                              Show this help message and exit.
-v, --version                           Show program's version number and exit.
-q, --quiet                             Enable quiet mode, i.e. nothing will be printed.
--verbose                               Print various debugging information, e.g. print traceback when there is an exception.
--log-level                             Set logging level: {debug,info,warning,error}. (default: info)
--log-format                            Set logging formatter: {console,only_msg,simple}. (default: simple)

HTTP requests options:

-u, --user-agent USER_AGENT             User Agent. (default: Mozilla/5.0 (X11; Linux x86_64) ...)
-t, --http-timeout TIMEOUT              HTTP timeout in seconds. (default: 120)
-d, --delay-requests DELAY              Delay in seconds between HTTP requests. (default: 2)

`:warning:` don't use a delay (``-d``) too short (e.g. 0.5 second between HTTP requests) because you will overwhelm the server and your IP address will eventually get banned.

`:star:`

  The following are **required** input/ouput arguments:
  
  - ``input_pickle_file`` is the path to the pickle file containing the list of URLs to theoretical physicists' Wikipedia pages.
  - ``output_directory`` is the path to the directory where the Wikipedia pages and corresponding images will be saved.

`:information_source:`

  Logging formatters to choose from:

  - **console**: ``%(asctime)s | %(levelname)-8s | %(message)s``
  - **only_msg**: ``%(message)s``
  - **simple**: ``%(levelname)-8s %(message)s``

Exercises
=========
Misc
----
1. Extract names from text [TODO]
'''''''''''''''''''''''''''''''''
`:warning:` TODO

2. Extract DOB and DOD from text [TODO]
'''''''''''''''''''''''''''''''''''''''
`:warning:` TODO

Wikipedia pages of theoretical physicists
-----------------------------------------
1. Get list of URLs to Wikipedia pages of theoretical physicists
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
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

  - The Python script can be found at `download_wiki_pages.py <https://github.com/raul23/web-crawler/blob/main/exercises/download_wiki_pages.py>`_ 
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
.. TODO: remove TODO in relative link eventually
Apart from the *DOB* and *DOD* extracted `previously <#extract-dob-and-dod-from-wikipedia-pages-todo>`_ from physicists' Wikipedia pages, there are more information that can be obtained from the information box:

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
