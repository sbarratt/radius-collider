#!/usr/bin/env python

"""Utilities
File with various useful functions.
"""

from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
import string
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re


def stem_tokens(tokens):
    """
    :param tokens: a list of tokens
    :return: a list of stemmed tokens
    """
    stemmer = nltk.stem.porter.PorterStemmer()
    return [stemmer.stem(item) for item in tokens]


def normalize(text):
    """
    remove punctuation, lowercase, and stem
    """
    remove_punctuation_map = dict((ord(char), None)
                                  for char in string.punctuation)
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))


def dotproduct(l1, l2):
    """
    :return: scalar of the dot product of the two lists
    """
    assert len(l1) == len(l2), "lists are different length"
    return float(np.array(l1).dot(np.array(l2)))


def cosine_sim(text1, text2):
    """
    :return: cosine similarity between text1 and text2
    """
    vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0, 1]


def removeNans(var):
    """
    prune NANs
    """
    if type(var) is not np.float64 or np.isnan(var):
        var = 0.0
    return float(var)


def word2vec_sim(text1, text2, model):
    w1 = filter(lambda x: x in model.vocab,
                clean_paragraph(text1))
    w2 = filter(lambda x: x in model.vocab,
                clean_paragraph(text2))
    if not w1 or not w2:
        return .1  # default value
    return model.n_similarity(w1, w2)


def add_synonyms(words):
    """ Return list of synonyms of words in words """
    more_words = []
    for word in words:
        nltk_id = word + '.n.01'  # TODO Might want to check if word is a noun or not
        try:
            synonyms = wn.synset(nltk_id).lemma_names()
            if type(synonyms) == str:
                more_words += [synonyms.replace('_', ' ')]
            else:
                for w in synonyms:
                    more_words += [w.replace('_', ' ')]
        except:
            more_words += [word]
    return more_words


def add_synonyms_to_text(text):
    """
    :param text: string
    :return: string containing original string with synonyms
    """
    return ' '.join(add_synonyms(clean_paragraph(text)))


def clean_paragraph(text):
    """
    Cleans and Tokenizes string
    """
    text = re.sub(r'\(except(.+?)\)', '', text)  # removes (except ...)

    tokenizer = RegexpTokenizer(r'\w+')
    stopset = set(stopwords.words('english'))
    wordnet_lemmatizer = WordNetLemmatizer()

    text.encode('utf-8', 'ignore')
    tokens = tokenizer.tokenize(text)  # tokenize
    tokens = [w for w in tokens if not w in stopset]  # remove stopwords
    x = []
    for word in tokens:
        if wordnet.synsets(word):  # only keep words in english dictionary
            if len(word) > 1:
                # lemmatize and lower case
                x.append(wordnet_lemmatizer.lemmatize(word.lower()))
    return x


def sample_weights(w=8, n=1000):
    """
    :param w: number of weights
    :param n: number of samples
    :return: list of weight dictionaries
    """
    l = []
    for i in xrange(n):
        z = np.random.rand(w)
        z = z / sum(z)
        features = {
            'd_d_sim': z[0],
            't_t_sim': z[1],
            'd_t_sim': z[2],
            't_d_sim': z[3],
            'd_d_w2v': z[4],
            't_t_w2v': z[5],
            'd_t_w2v': z[6],
            't_d_w2v': z[7]
        }
        l.append(features)
    return l


def bucket_guesses(guesses, threshold=0):
    """
    :param guesses: list of tuples (score, 6 digit NAICS code))
    :param threshold: limit to bucket above scores
    :return: list of tuples (summed score, 3 code NAICS code))
    """
    codes = {}
    for score, naic_code in guesses:
        if score > threshold:
            key = str(naic_code)[:3]
            codes[key] = score + codes[key] if key in codes else score

    code_list = sorted(codes.items(), key=lambda x: x[1], reverse=True)
    return code_list


def score_prediction(guess, actual):
    """
    :param guess: NAICS code
    :param actual: ground truth NAICS
    :return: score
    """
    assert actual is not None, 'Need a ground truth score'
    if guess == '' or guess is None:
        return 0
    if guess[:2] != actual[:2]:
        return -2
    score = 0
    for idx, c in enumerate(actual):
        if (idx + 1) > len(guess):
            break
        if c == guess[idx]:
            score += 1
        else:
            score -= 1
            break
    return score


def get_score_color(guess, actual):
    """
    :param guess: NAICS code
    :param actual: ground truth NAICS
    :return: color corresponding to the score for database.html
    """
    if actual == None:
        return '#DDDDDD'
    score = score_prediction(guess, actual)
    if score == 6:
        return '#004b31'
    elif score == 5:
        return '#006442'
    elif score == 4:
        return '#007e53'
    elif score == 3:
        return '#009764'
    elif score == 2:
        return '#00b174'
    elif score == 1:
        return '#00e495'
    elif score == 0:
        return '#ffe34c'
    elif score == -2:
        return '#b1003d'


if __name__ == '__main__':
    print add_synonyms(['dog'])
    print add_synonyms_to_text('dog')
    print clean_paragraph('Hi my name is John!!!!')
    print cosine_sim("cat", "cat is dog")
