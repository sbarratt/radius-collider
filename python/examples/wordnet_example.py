"""
Example of Wordnet.
Type in two words and get the similarity between them

In short, WordNet is a database of English words that are linked together by
their semantic relationships. It is like a supercharged dictionary/thesaurus
with a graph structure.
"""

from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic
from nltk.corpus import genesis
import IPython as ipy


def get_first_synset(string):
    a = wn.synsets(string)
    if type(a) == list:
        return a[0]
    else:
        return a

# Load Information Contents
brown_ic = wordnet_ic.ic('ic-brown.dat')
semcor_ic = wordnet_ic.ic('ic-semcor.dat')
genesis_ic = wn.ic(genesis, False, 0.0)

while 1:
    item1 = raw_input()
    item2 = raw_input()

    item1_ss = get_first_synset(item1)
    item2_ss = get_first_synset(item2)
    print "Path Similarity:", item1_ss.path_similarity(item2_ss)  # 126 us
    print "Leacock-Chodorow:", item1_ss.lch_similarity(item2_ss)  # 135 us
    print "Wu-Palmer:", item1_ss.wup_similarity(item2_ss)  # 772 us
    # 14.0 us
    print "Resnik Brown:", item1_ss.res_similarity(item2_ss, brown_ic)
    # 14.1 us
    print "Resnik Semcor:", item1_ss.res_similarity(item2_ss, semcor_ic)
    # 14.9 us
    print "Jiang-Conrath Brown:", item1_ss.jcn_similarity(item2_ss, brown_ic)
    # 14.9 us
    print "Jiang-Conrath Genesis:", item1_ss.jcn_similarity(item2_ss, genesis_ic)
    # 14.7 us
    print "Lin semcor:", item1_ss.lin_similarity(item2_ss, semcor_ic)

# morphy
