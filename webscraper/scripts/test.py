import os
import pickle
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
import ipdb
# ipdb.set_trace()

# https://en.wikipedia.org/wiki/List_of_theoretical_physicists
# https://en.wikipedia.org/wiki/List_of_physicists
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

if True:
    '''
    Example: Erwin Schrödinger
    https://en.wikipedia.org/wiki/Erwin_Schr%C3%B6dinger

    12 August 1887 – 4 January 1961

    Born	Erwin Rudolf Josef Alexander Schrödinger
            12 August 1887

    Died	4 January 1961 (aged 73)
            Vienna, Austria


    Schrödinger was born in Erdberg [de], Vienna, Austria, on 12 August 1887,

    He died in Vienna of tuberculosis when he was 73.

    ############################################################
    Example: Rudolf Clausius
    https://en.wikipedia.org/wiki/Rudolf_Clausius

    2 January 1822 – 24 August 1888

    Born	2 January 1822
            Köslin, Province of Pomerania, Prussia (present-day Koszalin, Poland)

    Died	24 August 1888 (aged 66)

    Two years later, on 24 August 1888, he died in Bonn, Germany.

    ############################################################
    Example: Richard M. Friedberg
    https://en.wikipedia.org/wiki/Richard_M._Friedberg

    born October 8, 1935

    Born	8 October 1935 (age 87)

    Friedberg was born in Manhattan on Oct 8, 1935 ...


    ############################################################
    Example: Eugene Wigner
    https://en.wikipedia.org/wiki/Eugene_Wigner

    November 17, 1902 – January 1, 1995

    Born	Wigner Jenő Pál
            November 17, 1902
            Budapest, Kingdom of Hungary, Austria-Hungary

    Died	January 1, 1995 (aged 92)
            Princeton, New Jersey, U.S.

    Wigner died of pneumonia at the University Medical Center in Princeton, New Jersey on 1 January 1995.

    ############################################################
    Example: Xi Yin
    https://en.wikipedia.org/wiki/Xi_Yin

    born December 1983

    Born	December 1984 (age 37–38)

    ############################################################
    Example: Basilis C. Xanthopoulos
    https://en.wikipedia.org/wiki/Basilis_C._Xanthopoulos

    8 April 1951 – 27 November 1990

    Born	April 8, 1951
            Drama, Greece

    Died	November 27, 1991 (aged 40)
            Heraklion, Greece

    He served as a Chairman of department from 1987 until his murder on the evening of November 27, 1990, shot 
    together with his colleague Stephanos Pnevmatikos while giving a seminar by a 32-year-old disgruntled 
    mentally unstable named Giorgos Petrodaskalakis (who later committed suicide).
    '''

ipdb.set_trace()