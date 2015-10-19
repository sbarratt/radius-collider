from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from gensim.models import word2vec
import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer
import bisect
import IPython as ipy

def stem_tokens(tokens):
  stemmer = nltk.stem.porter.PorterStemmer()
  return [stemmer.stem(item) for item in tokens]

'''remove punctuation, lowercase, stem'''
def normalize(text):
  remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
  return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

def dotproduct(l1, l2):
  assert len(l1) == len(l2), "lists are different length"
  return sum([l1[i]*l2[i] for i in range(len(l1))])

def cosine_sim(text1, text2):
  """ Return the cosine similarity between text1 and text2 """
  vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')
  tfidf = vectorizer.fit_transform([text1, text2])
  return ((tfidf * tfidf.T).A)[0,1]

def word2vec_sim(text1, text2):
  sentences = word2vec.Text8Corpus('data/text8')
  print "laoded text corpus"
  model = word2vec.Word2Vec(sentences, size=200)
  return model.n_similarity(clean_paragraph(text1), clean_paragraph(text2))

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

  text.encode('utf-8', 'ignore')
  tokens = tokenizer.tokenize(text) #tokenize
  tokens = [w for w in tokens if not w in stopset] #remove stopwords
  x = []
  for word in tokens:
    if wordnet.synsets(word): #only keep words in english dictionary
      if len(word) > 1:
        x.append(wordnet_lemmatizer.lemmatize(word.lower())) #lemmatize and lower case
  return x

def bucket_guesses(guesses, threshold=0):
  codes = {}
  for score, naic in guesses:
    if score > threshold:
      key = str(naic['code'])[:3]
      codes[key] = score + codes[key] if key in codes else score

  code_list = sorted(codes.items(), key=lambda x: x[1], reverse=True)
  return code_list

if __name__ == '__main__':
  print word2vec_sim("cat", "cat is a dog")
  print add_synonyms(['dog'])
  print add_synonyms_to_text('dog')
  print clean_paragraph('Hi my name is John!!!!')
  print cosine_sim("cat", "cat is dog")
