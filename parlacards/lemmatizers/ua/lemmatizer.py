from uk_stemmer import UkStemmer

from parlacards.lemmatizers.ua.stop_words import STOPWORDS

def get_stopwords():
    return STOPWORDS

# initialize the stemmer class only once
stemmer = UkStemmer()
def lemmatize(token):
    return stemmer.stem_word(token)

def lemmatize_many(tokens):
    return [stemmer.stem_word(x) for x in tokens]
