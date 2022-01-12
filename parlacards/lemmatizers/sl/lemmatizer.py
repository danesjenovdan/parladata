from tagger.lemmatiser import Lemmatiser

from parlacards.lemmatizers.sl.stop_words import STOPWORDS


def get_stopwords():
    return STOPWORDS

# initialize the lemmatizer class only once
lemmatiser = Lemmatiser()
def lemmatize(token):
    return lemmatiser.lemmatise_token(token)[0][1]

def lemmatize_many(tokens):
    return [x[1] for x in lemmatiser.tag_lemmatise_sent(tokens)]
