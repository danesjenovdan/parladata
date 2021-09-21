from uk_stemmer import UkStemmer


# initialize the lemmatizer class only once
stemmer = UkStemmer()
def lemmatize(token):
    return stemmer.stem_word(token)

def lemmatize_many(tokens):
    return [stemmer.stem_word(x) for x in tokens]
