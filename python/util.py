from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer

from urllib import urlopen
from bs4 import BeautifulSoup
import json

import IPython as ipy

def stem_tokens(tokens):
  stemmer = nltk.stem.porter.PorterStemmer()
  return [stemmer.stem(item) for item in tokens]

'''remove punctuation, lowercase, stem'''
def normalize(text):
  remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
  return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

def cosine_sim(text1, text2):
  """ Return the cosine similarity between text1 and text2 """
  vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')
  tfidf = vectorizer.fit_transform([text1, text2])
  return ((tfidf * tfidf.T).A)[0,1]

def add_synonyms(words):
  """ Return list of synonyms of words in words """
  more_words = []
  for word in words:
    nltk_id = word + '.n.01' # TODO Might want to check if word is a noun or not
    try:
      synonyms = wn.synset(nltk_id).lemma_names()
      if type(synonyms) == str:
        more_words += [synonyms.replace('_',' ')]
      else:
        for w in synonyms:
          more_words += [w.replace('_',' ')]
    except:
      more_words += [word]
  return more_words

def add_synonyms_to_text(text):
  return ' '.join(add_synonyms(clean_paragraph(text)))

def clean_paragraph(text):
  """ Cleans and Tokenizes text (str) """

  tokenizer = RegexpTokenizer(r'\w+')
  stopset = set(stopwords.words('english'))
  wordnet_lemmatizer = WordNetLemmatizer()

  text.decode('utf-8')
  tokens = tokenizer.tokenize(text) #tokenize
  tokens = [w for w in tokens if not w in stopset] #remove stopwords
  x = []
  for word in tokens:
    if wordnet.synsets(word): #only keep words in english dictionary
      if len(word) > 1:
        x.append(wordnet_lemmatizer.lemmatize(word.lower())) #lemmatize and lower case
  return x

def get_tokenized_url_content(url):
  html = urlopen(url).read().decode('utf8')
  raw = BeautifulSoup(html).get_text()
  return clean_paragraph(raw)

def get_naics_data_for_level(code_length):
  with open('../naics_list.json', 'r') as jsonfile:
    naics_data = json.load(jsonfile)
  results = []
  for naics_item in naics_data:
    if len(str(naics_item['code'])) == code_length:
      results.append(naics_item)
  return results

if __name__ == '__main__':
  print add_synonyms(['dog'])
  print add_synonyms_to_text('dog')
  print clean_paragraph('Hi my name is John!!!!')
  print cosine_sim("cat", "cat is dog")
  # print get_tokenized_url_content('http://www.shanebarratt.com')
