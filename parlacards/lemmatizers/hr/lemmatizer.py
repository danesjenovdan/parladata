from parlacards.lemmatizers.classla import ClasslaLemmatizer
from parlacards.lemmatizers.sl.stop_words import STOPWORDS


def get_stopwords():
    return STOPWORDS

# initialize the lemmatizer class only once
lemmatiser = ClasslaLemmatizer("hr")

def lemmatize_many(speech):
    return " ".join(lemmatiser.lemmatize(speech))
