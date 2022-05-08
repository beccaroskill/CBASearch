import json
import os
from spacy.lang.en import English
import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet as wn
nltk.download('stopwords')
from nltk.stem.wordnet import WordNetLemmatizer
from gensim import corpora
import gensim
import roman

all_headers = []
structured_folder = 'DOL_Scrape/ContractText_Structured'
for file_name in os.listdir(structured_folder):
    with open(os.path.join(structured_folder, file_name)) as f:
        file_structure = json.load(f)
        all_headers += [h.strip() for h, _ in file_structure if h]


def tokenize(text):
    lda_tokens = []
    tokens = parser(text)
    for token in tokens:
        if token.orth_.isspace():
            continue
        elif token.like_url:
            lda_tokens.append('URL')
        elif token.orth_.startswith('@'):
            lda_tokens.append('SCREEN_NAME')
        else:
            lda_tokens.append(token.lower_)
    return lda_tokens

def get_lemma(word):
    lemma = wn.morphy(word)
    if lemma is None:
        return word
    else:
        return lemma
    
def get_lemma2(word):
    return WordNetLemmatizer().lemmatize(word)

def prepare_text_for_lda(text):
    tokens = tokenize(text)
    tokens = [token for token in tokens if len(token) > 4]
    tokens = [token for token in tokens if token not in en_stop]
    tokens = [get_lemma(token) for token in tokens]
    return tokens

parser = English()
header_data = []
custom_stop = ['article', 'union', 'employer', 'employee'] + [roman.toRoman(x).lower() for x in range(100)]
en_stop = set(nltk.corpus.stopwords.words('english') + custom_stop)
for header in all_headers:
    tokens = prepare_text_for_lda(header)
    header_data.append(tokens)
    
    
dictionary = corpora.Dictionary(header_data)
corpus = [dictionary.doc2bow(text) for text in header_data]


NUM_TOPICS = 10
ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics = NUM_TOPICS, id2word=dictionary, passes=15)
topics = ldamodel.print_topics(num_words=4)
for topic in topics:
    print(topic)

for header in all_headers:
    tokens = prepare_text_for_lda(header)
    header_data = tokens
        
    dictionary = corpora.Dictionary([header_data])
    corpus = dictionary.doc2bow(header_data) 
    topics = ldamodel.get_document_topics(corpus)
    print(header)
    print(topics, '\n\n')
