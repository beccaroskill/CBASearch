import os
import json
import spacy
# nlp = spacy.load("en_core_web_sm")
from spacy.lang.en import English
import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet as wn
nltk.download('stopwords')
from nltk.stem.wordnet import WordNetLemmatizer
from gensim import corpora
import gensim
import pickle
import roman

def add_to_header(line, header, body):
   if '###' == line[:3]:
       if 'article' in line.lower() or \
                   'article' in header.lower() and not body:
           return True
   return False

def process_section(header, body):
    if 0.5*len(body)>len(header) and len(header.split('\n'))<=5:
        check_lines = body.split('\n')[:7]
        starts_w_article_count = len([x for x in check_lines if 'article' in x[:15].lower()\
                                                                  or 'side letter' in x[:20].lower()])
        total_count = len([x for x in check_lines if x.strip()])
        if starts_w_article_count > 0.4*total_count:
            return ['', section_header+section_body]
        return [section_header, section_body]
    else:
        return ['', section_header+section_body]

txt_folder = 'DOL_Scrape/ContractText'
structured_folder = 'DOL_Scrape/ContractText_Structured'
all_headers = []

for file_path in os.listdir(txt_folder): 
    txt_path = os.path.join(txt_folder, file_path)
    file_structure = []
    section_header = ''
    section_body = ''
    with open(txt_path) as txt_f:
        lines = txt_f.readlines()
        for line in lines:
            if add_to_header(line, section_header, section_body):
                line = line[4:]
                if section_body:
                    file_structure.append(process_section(section_header, section_body))
                    section_header = ''
                    section_body = ''
                section_header += line
            else:
                if '###' == line[:3]:
                    line = line[4:]
                section_body += line
    all_headers += [h.strip() for h, _ in file_structure if h]
    # with open(os.path.join(structured_folder, file_path[:-4] + '.json'), 'w') as f:
    #     json.dump(file_structure, f)

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
# pickle.dump(corpus, open('corpus.pkl', 'wb'))
# dictionary.save('dictionary.gensim')
NUM_TOPICS = 10
ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics = NUM_TOPICS, id2word=dictionary, passes=15)
# ldamodel.save('model5.gensim')
topics = ldamodel.print_topics(num_words=4)
for topic in topics:
    print(topic)
print('\n\n\n')


for header in all_headers:
    tokens = prepare_text_for_lda(header)
    header_data = tokens
        
    dictionary = corpora.Dictionary([header_data])
    corpus = dictionary.doc2bow(header_data) 
    topics = ldamodel.get_document_topics(corpus)
    print(header)
    print(topics, '\n\n')
    # pickle.dump(corpus, open('corpus.pkl', 'wb'))