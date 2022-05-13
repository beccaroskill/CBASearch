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

all_sections = []
structured_folder = 'DOL_Scrape/ContractText_Structured'
for file_name in os.listdir(structured_folder):
    if 'json' in file_name:
        with open(os.path.join(structured_folder, file_name)) as f:
            file_structure = json.load(f)
            all_sections += [h + b for h, b in file_structure if h]


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
section_data = []
custom_stop = ['article', 'union', 'employer', 'employee'] + [roman.toRoman(x).lower() for x in range(100)]
en_stop = set(nltk.corpus.stopwords.words('english') + custom_stop)
for section in all_sections:
    tokens = prepare_text_for_lda(section)
    section_data.append(tokens)
    
    
dictionary = corpora.Dictionary(section_data)
corpus = [dictionary.doc2bow(text) for text in section_data]


NUM_TOPICS = 10
ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics = NUM_TOPICS, id2word=dictionary, passes=15)
topics = ldamodel.print_topics(num_words=4)
for topic in topics:
    print(topic)

for section in all_sections[:10]:
    tokens = prepare_text_for_lda(section)
    header_data = tokens
        
    dictionary = corpora.Dictionary([section])
    corpus = dictionary.doc2bow(header_data) 
    topics = ldamodel.get_document_topics(corpus)
    print(section)
    print(topics, '\n\n')

# Headers only

# (0, '0.130*"recognition" + 0.069*"hire" + 0.052*"contract" + 0.051*"termination"')
# (1, '0.111*"dispute" + 0.086*"overtime" + 0.062*"jurisdictional" + 0.055*"shift"')
# (2, '0.120*"management" + 0.096*"wages" + 0.096*"right" + 0.071*"rates"')
# (3, '0.111*"strike" + 0.079*"lockout" + 0.055*"insurance" + 0.051*"payment"')
# (4, '0.108*"grievance" + 0.108*"benefit" + 0.107*"procedure" + 0.082*"fringe"')
# (5, '0.068*"training" + 0.064*"pension" + 0.046*"apprentice" + 0.040*"deduction"')
# (6, '0.100*"safety" + 0.066*"savings" + 0.064*"steward" + 0.057*"clause"')
# (7, '0.102*"security" + 0.085*"conditions" + 0.082*"working" + 0.060*"holiday"')
# (8, '0.073*"hours" + 0.068*"foreman" + 0.064*"section" + 0.044*"subcontractor"')
# (9, '0.211*"agreement" + 0.077*"jurisdiction" + 0.064*"scope" + 0.048*"period"')

# All text

# (0, '0.018*"concrete" + 0.017*"include" + 0.016*"material" + 0.013*"construction"')
# (1, '0.045*"benefit" + 0.028*"participant" + 0.022*"service" + 0.015*"shall"')
# (2, '0.038*"leave" + 0.035*"shall" + 0.025*"member" + 0.017*"school"')
# (3, '0.058*"shall" + 0.042*"employee" + 0.028*"hours" + 0.024*"holiday"')
# (4, '0.059*"shall" + 0.030*"section" + 0.023*"employee" + 0.019*"steward"')
# (5, '0.034*"shall" + 0.031*"agreement" + 0.020*"contribution" + 0.019*"trust"')
# (6, '0.040*"shall" + 0.019*"apprentice" + 0.018*"engineer" + 0.018*"contractor"')
# (7, '0.023*"shall" + 0.019*"player" + 0.019*"company" + 0.012*"employee"')
# (8, '0.050*"shall" + 0.043*"agreement" + 0.022*"party" + 0.013*"grievance"')
# (9, '0.073*"hours" + 0.070*"shall" + 0.061*"shift" + 0.025*"overtime"')