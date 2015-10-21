from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer
import IPython as ipy
import numpy as np

def stem_tokens(tokens):
  stemmer = nltk.stem.porter.PorterStemmer()
  return [stemmer.stem(item) for item in tokens]

'''remove punctuation, lowercase, stem'''
def normalize(text):
  remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
  return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

def dotproduct(l1, l2):
  assert len(l1) == len(l2), "lists are different length"
  return float(np.array(l1).dot(np.array(l2)))

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

  text.encode('utf-8', 'ignore')
  tokens = tokenizer.tokenize(text) #tokenize
  tokens = [w for w in tokens if not w in stopset] #remove stopwords
  x = []
  for word in tokens:
    if wordnet.synsets(word): #only keep words in english dictionary
      if len(word) > 1:
        x.append(wordnet_lemmatizer.lemmatize(word.lower())) #lemmatize and lower case
  return x

def sample_weights(w=8, n=1000):
  l = []
  for i in range(n):
    z = np.random.rand(w)
    z = z/sum(z)
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
  codes = {}
  for score, naic_code in guesses:
    if score > threshold:
      key = str(naic_code)[:3]
      codes[key] = score + codes[key] if key in codes else score

  code_list = sorted(codes.items(), key=lambda x: x[1], reverse=True)
  return code_list

def score_prediction(guess, actual):
  assert actual is not None, 'Need a ground truth score'
  if guess == '' or guess is None:
    return 0
  if guess[:2] != actual[:2]:
    return -2
  sum = 0
  for idx, c in enumerate(actual):
    if (idx + 1) > len(guess):
      break
    if c == guess[idx]:
      sum += 1
    else:
      sum -= 1
      break
  return sum

if __name__ == '__main__':
  print add_synonyms(['dog'])
  print add_synonyms_to_text('dog')
  print clean_paragraph('Hi my name is John!!!!')
  print cosine_sim("cat", "cat is dog")
