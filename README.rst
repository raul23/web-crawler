=====================
Web crawler + scraper
=====================
.. contents:: **Contents**
   :depth: 4
   :local:
   :backlinks: top

Scripts
=======
``get_physicists_urls.py``: Get list of URLs to Wikipedia pages of theoretical physicists
-----------------------------------------------------------------------------------------
Starting from `Category:Theoretical physicists <https://en.wikipedia.org/w/index.php?title=Category:Theoretical_physicists>`_, get all the absolute URLs of theoretical physicists' Wikipedia pages by processing the list of relative URLs in the section **Pages in category "Theoretical physicists"** and crawling through the next pages until no more *next page* is found.

This script outputs a list of URLs to Wikipedia pages of theoretical physicsts that is saved as a pickle file.

`:information_source:`

  - The Python script can be found at `get_physicists_urls.py <./exercises/get_physicists_urls.py>`_
  - The Python script saves the list of URLs as a pickle file
  - For more information about the script's usage, check the `Usage <#usage-for-get-physicists-urls-py>`_ section.

Dependencies
''''''''''''
This is the environment on which the script was tested:

* **Platforms:** macOS
* **Python**: versions **3.7** and **3.8**
* `beautifulsoup4 <https://www.crummy.com/software/BeautifulSoup/>`_ **v4.11.1**, for screen-scraping

`:information_source:` The built-in module ``urllib`` is used for sending HTTP requests.

Usage for ``get_physicists_urls.py``
''''''''''''''''''''''''''''''''''''
Run the script ``get_physicists_urls.py``
`````````````````````````````````````````
Run the script by specifying the path of the pickle that will contain the list of URLs::

   $ pyton get_physicists_urls.py ~/Data/wikipedia/list_physicists_urls.pkl -d 3

Showing the first 4 URLs in the list::

   ipdb> list_physicists_urls[:4]
   
   ['https://en.wikipedia.org//wiki/Alexei_Abrikosov_(physicist)', 'https://en.wikipedia.org//wiki/Vadym_Adamyan', 'https://en.wikipedia.org//wiki/David_Adler_(physicist)', 'https://en.wikipedia.org//wiki/Diederik_Aerts']

`:information_source:`

  - ``~/Data/wikipedia/list_physicists_urls.pkl``: pickle file that will contain the list of URLs to Wikipedia 
    pages of theoretical physicists
  - ``-d 3``: three seconds between HTTP requests 
   
  Check `List of options <#list-of-options-for-get-physicists-urls-py>`_ to know more about the other options you can use.

List of options for ``get_physicists_urls.py``
``````````````````````````````````````````````
To display the script's list of options and their descriptions, use the ``-h`` option::

   $ pyton get_physicists_urls.py -h

   usage: python get_physicists_urls.py [OPTIONS] {pickle_file}

   Get URLs to Wikipedia pages of theoretical physicists

   positional arguments:
     pickle_file           Path to the pickle file that will contain the list of URLs to theoretical physicists' Wikipedia pages.

   optional arguments:
     -h, --help            show this help message and exit
     -d DELAY, --delay-requests DELAY
                           Delay in seconds between HTTP requests. (default: 2)

`:warning:` Don't use a delay (``-d``) too short (e.g. 0.5 second between HTTP requests) because you will overwhelm the server and your IP address will eventually get banned.

``download_wiki_pages.py``: Download Wikipedia pages of theoretical physicists
------------------------------------------------------------------------------
This script takes as input a pickle file containing URLs to Wikipedia pages of theoretical physicists (see the script `get_physicists_urls.py <#get-physicists-urls-py-get-list-of-urls-to-wikipedia-pages-of-theoretical-physicists>`_).

`:information_source:`

  - The Python script can be found at `download_wiki_pages.py <./exercises/download_wiki_pages.py>`_ 
  - By default, there is a delay of 2 seconds between HTTP requests.
  - For more information about the script's usage, check the `Usage <#usage-for-download-wiki-pages-py>`_ section.

Here are the general steps for downloading the Wikipedia pages with the corresponding images:

1. Load the pickle file containing the list of URLs which was generated from the `previous script <#get-physicists-urls-py-get-list-of-urls-to-wikipedia-pages-of-theoretical-physicists>`_
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

Dependencies
''''''''''''
This is the environment on which the script was tested:

* **Platforms:** macOS
* **Python**: versions **3.7** and **3.8**
* `requests <https://requests.readthedocs.io/en/latest/>`_: **v2.28.1**, for sending HTTP GET requests
* `beautifulsoup4 <https://www.crummy.com/software/BeautifulSoup/>`_ **v4.11.1**, for screen-scraping

Usage for ``download_wiki_pages.py``
''''''''''''''''''''''''''''''''''''
Run the script ``download_wiki_pages.py``
``````````````````````````````````````````
Run the script by specifying the paths to the `pickle file <#get-list-of-urls-to-wikipedia-pages-of-theoretical-physicists>`_ and the ouput directory where the downloaded Wikipedia pages will be saved::

   $ pyton download_wiki_pages.py ~/Data/wikipedia/list_physicists_urls.pkl ~/Data/wikipedia/physicists/ --log-format only_msg --log-level debug
   
`:information_source:`

  - ``~/Data/wikipedia/list_physicists_urls.pkl``: pickle file containing list of URLs to Wikipedia 
    pages of theoretical physicists (See `Exercise 1 <#get-list-of-urls-to-wikipedia-pages-of-theoretical-physicists>`_)
  - ``~/Data/wikipedia/physicists/``: ouput directory where the downloaded Wikipedia pages will be saved
  - ``--log-format only_msg``: display only the logging message without the timestamp or the logging level
  - ``--log-level debug``: display all logging messages with the ``debug`` logging level
   
  Check `List of options <#list-of-options-for-download-wiki-pages-py>`_ to know more about the other options you can use.
   
`:star:` In order to stop the script at any moment, press ``ctrl`` + ``c``.

List of options for ``download_wiki_pages.py``
``````````````````````````````````````````````
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

`:warning:` Don't use a delay (``-d``) too short (e.g. 0.5 second between HTTP requests) because you will overwhelm the server and your IP address will eventually get banned.

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
1. Extract DOB and DOD from Wikipedia pages [TODO]
--------------------------------------------------
`:information_source:`

  - **DOB:** *Date of Birth*
  - **DOD:** *Date of Death*

`:warning:` TODO

2. Extract more information from the information box [TODO]
-----------------------------------------------------------
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
