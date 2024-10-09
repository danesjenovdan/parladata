import classla

class ClasslaLemmatizer:
    nlp = None
    def __init__(self, language_code):
        if not ClasslaLemmatizer.nlp:
            classla.download(language_code)
            ClasslaLemmatizer.nlp = classla.Pipeline(language_code, processors="tokenize,pos,lemma")

    def lemmatize(self, text):
        doc = self.nlp(text)
        return [word.lemma for word in doc.iter_words() if word.upos != "PUNCT"]

