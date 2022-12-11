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
   
