#!/usr/bin/env python
import argparse
import time

import nltk
from nameparser.parser import HumanName

import ipdb

# Examples
text1 = """
Wolfgang Ernst Pauli (/ˈpɔːli/; German: [ˈvɔlfɡaŋ ˈpaʊli]; 25 April 1900 – 
15 December 1958) was an Austrian theoretical physicist and one of the pioneers 
of quantum physics. In 1945, after having been nominated by Albert Einstein, 
Pauli received the Nobel Prize in Physics for his "decisive contribution 
through his discovery of a new law of Nature, the exclusion principle or Pauli 
principle". The discovery involved spin theory, which is the basis of a theory 
of the structure of matter.
"""

text2 = """
Anderson was born in Indianapolis, Indiana, and grew up in Urbana, Illinois. 
His father, Harry Warren Anderson, was a professor of plant pathology at the 
University of Illinois at Urbana; his maternal grandfather was a mathematician 
at Wabash College, where Anderson's father studied; and his maternal uncle was 
a Rhodes Scholar who became a professor of English, also at Wabash College. He 
graduated from University Laboratory High School in Urbana in 1940. Under the 
encouragement of a math teacher by the name of Miles Hartley, Anderson enrolled 
at Harvard University to study under a fully-funded scholarship. He 
concentrated in "Electronic Physics" and completed his B.S. in 1943, after which 
he was drafted into the war effort and built antennas at the Naval Research 
Laboratory until the end of the Second World War in 1945. As an undergraduate, 
his close associates included particle-nuclear physicist H. Pierre Noyes, 
philosopher and historian of science Thomas Kuhn and molecular physicist Henry 
Silsbee. After the war, Anderson returned to Harvard to pursue graduate studies 
in physics under the mentorship of John Hasbrouck van Vleck; he received his 
Ph.D. in 1949 after completing a doctoral dissertation titled "The theory of 
pressure broadening of spectral lines in the microwave and infrared regions."
"""

text3 = """
Galileo continued to receive visitors until 1642, when, after suffering fever 
and heart palpitations, he died on 8 January 1642, aged 77. The Grand Duke of 
Tuscany, Ferdinando II, wished to bury him in the main body of the Basilica of 
Santa Croce, next to the tombs of his father and other ancestors, and to erect 
a marble mausoleum in his honour.

These plans were dropped, however, after Pope Urban VIII and his nephew, 
Cardinal Francesco Barberini, protested, because Galileo had been condemned by 
the Catholic Church for "vehement suspicion of heresy". He was instead buried 
in a small room next to the novices' chapel at the end of a corridor from the 
southern transept of the basilica to the sacristy. He was reburied in the main 
body of the basilica in 1737 after a monument had been erected there in his 
honour; during this move, three fingers and a tooth were removed from his 
remains. These fingers are currently on exhibition at the Museo Galileo in 
Florence, Italy.
"""

text4 = """
Some economists have responded positively to Bitcoin, including 
Francois R. Velde, senior economist of the Federal Reserve in Chicago 
who described it as "an elegant solution to the problem of creating a 
digital currency." In November 2013 Richard Branson announced that 
Virgin Galactic would accept Bitcoin as payment, saying that he had invested 
in Bitcoin and found it "fascinating how a whole new global currency 
has been created", encouraging others to also invest in Bitcoin.
Other economists commenting on Bitcoin have been critical. 
Economist Paul Krugman has suggested that the structure of the currency 
incentivizes hoarding and that its value derives from the expectation that 
others will accept it as payment. Economist Larry Summers has expressed 
a "wait and see" attitude when it comes to Bitcoin. Nick Colas, a market 
strategist for ConvergEx Group, has remarked on the effect of increasing 
use of Bitcoin and its restricted supply, noting, "When incremental 
adoption meets relatively fixed supply, it should be no surprise that 
prices go up. And that’s exactly what is happening to BTC prices."
"""


def download_packages():
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')


# Method 1, ref.: https://stackoverflow.com/q/20290870
def get_human_names(text):
    tokens = nltk.tokenize.word_tokenize(text)
    pos = nltk.pos_tag(tokens)
    sentt = nltk.ne_chunk(pos, binary=False)
    person_list = []
    person = []
    name = ""
    for subtree in sentt.subtrees(filter=lambda t: t.label() == 'PERSON'):
        for leaf in subtree.leaves():
            person.append(leaf[0])
        if len(person) > 1:  # avoid grabbing lone surnames
            for part in person:
                name += part + ' '
            if name[:-1] not in person_list:
                person_list.append(name[:-1])
            name = ''
        person = []

    return person_list


def setup_argparser():
    msg = 'Get names from texts'
    parser = argparse.ArgumentParser(
        description='',
        usage=f"python %(prog)s [OPTIONS]\n\n{msg}",
        # ArgumentDefaultsHelpFormatter
        # HelpFormatter
        # RawDescriptionHelpFormatter
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-m', '--method', metavar='METHOD', dest='method', choices=[1],
                        default=1, type=int, help='Method to use for extracting the names from texts.')
    parser.add_argument(
        '-d', '--download', action='store_true',
        help='Whether to download the nltk packages: punkt, averaged_perceptron_tagger, '
             'maxent_ne_chunker, words')
    return parser


if __name__ == '__main__':
    parser = setup_argparser()
    args = parser.parse_args()
    texts = [text1, text2, text3, text4]
    if args.download:
        download_packages()
    print(f'Extracting names with method #{args.method}\n')
    time.sleep(1)
    for i, text in enumerate(texts, start=1):
        names = get_human_names(text)
        print("#########")
        print(f'# Text{i} #')
        print("#########")
        if args.method == 1:
            print("LAST, FIRST")
            print("-----------")
            for name in names:
                last_first = HumanName(name).last + ', ' + HumanName(name).first
                print(last_first)
            print()
        else:
            print(f'Unsupported method #{args.method}')
