from datetime import datetime, timedelta
from string import punctuation

from tagger.lemmatiser import Lemmatiser

slovenian_stopwords = ['a', 'ali', 'april', 'avgust', 'b', 'bi', 'bil', 'bila', 'bile', 'bili', 'bilo', 'biti', 'blizu', 'bo', 'bodo', 'bojo', 'bolj', 'bom', 'bomo', 'boste', 'bova', 'boš', 'brez', 'c', 'cel', 'cela', 'celi', 'celo', 'd', 'da', 'daleč', 'dan', 'danes', 'datum', 'december', 'deset', 'deseta', 'deseti', 'deseto', 'devet', 'deveta', 'deveti', 'deveto', 'do', 'dober', 'dobra', 'dobri', 'dobro', 'dokler', 'dol', 'dolg', 'dolga', 'dolgi', 'dovolj', 'drug', 'druga', 'drugi', 'drugo', 'dva', 'dve', 'e', 'eden', 'en', 'ena', 'ene', 'eni', 'enkrat', 'eno', 'etc.', 'f', 'februar', 'g', 'g.', 'ga', 'ga.', 'gor', 'gospa', 'gospod', 'h', 'halo', 'i', 'idr.', 'ii', 'iii', 'in', 'iv', 'ix', 'iz', 'j', 'januar', 'jaz', 'je', 'ji', 'jih', 'jim', 'jo', 'julij', 'junij', 'jutri', 'k', 'kadarkoli', 'kaj', 'kajti', 'kako', 'kakor', 'kamor', 'kamorkoli', 'kar', 'karkoli', 'katerikoli', 'kdaj', 'kdo', 'kdorkoli', 'ker', 'ki', 'kje', 'kjer', 'kjerkoli', 'ko', 'koder', 'koderkoli', 'koga', 'komu', 'kot', 'kratek', 'kratka', 'kratke', 'kratki', 'l', 'lahka', 'lahke', 'lahki', 'lahko', 'le', 'lep', 'lepa', 'lepe', 'lepi', 'lepo', 'leto', 'm', 'maj', 'majhen', 'majhna', 'majhni', 'malce', 'malo', 'manj', 'marec', 'me', 'med', 'medtem', 'mene', 'mesec', 'mi', 'midva', 'midve', 'mnogo', 'moj', 'moja', 'moje', 'mora', 'morajo', 'moram', 'moramo', 'morate', 'moraš', 'morem', 'mu', 'n', 'na', 'nad', 'naj', 'najina', 'najino', 'najmanj', 'naju', 'največ', 'nam', 'narobe', 'nas', 'nato', 'nazaj', 'naš', 'naša', 'naše', 'ne', 'nedavno', 'nedelja', 'nek', 'neka', 'nekaj', 'nekatere', 'nekateri', 'nekatero', 'nekdo', 'neke', 'nekega', 'neki', 'nekje', 'neko', 'nekoga', 'nekoč', 'ni', 'nikamor', 'nikdar', 'nikjer', 'nikoli', 'nič', 'nje', 'njega', 'njegov', 'njegova', 'njegovo', 'njej', 'njemu', 'njen', 'njena', 'njeno', 'nji', 'njih', 'njihov', 'njihova', 'njihovo', 'njiju', 'njim', 'njo', 'njun', 'njuna', 'njuno', 'no', 'nocoj', 'november', 'npr.', 'o', 'ob', 'oba', 'obe', 'oboje', 'od', 'odprt', 'odprta', 'odprti', 'okoli', 'oktober', 'on', 'onadva', 'one', 'oni', 'onidve', 'osem', 'osma', 'osmi', 'osmo', 'oz.', 'p', 'pa', 'pet', 'peta', 'petek', 'peti', 'peto', 'po', 'pod', 'pogosto', 'poleg', 'poln', 'polna', 'polni', 'polno', 'ponavadi', 'ponedeljek', 'ponovno', 'potem', 'povsod', 'pozdravljen', 'pozdravljeni', 'prav', 'prava', 'prave', 'pravi', 'pravo', 'prazen', 'prazna', 'prazno', 'prbl.', 'precej', 'pred', 'prej', 'preko', 'pri', 'pribl.', 'približno', 'primer', 'pripravljen', 'pripravljena', 'pripravljeni', 'proti', 'prva', 'prvi', 'prvo', 'r', 'ravno', 'redko', 'res', 'reč', 's', 'saj', 'sam', 'sama', 'same', 'sami', 'samo', 'se', 'sebe', 'sebi', 'sedaj', 'sedem', 'sedma', 'sedmi', 'sedmo', 'sem', 'september', 'seveda', 'si', 'sicer', 'skoraj', 'skozi', 'slab', 'smo', 'so', 'sobota', 'spet', 'sreda', 'srednja', 'srednji', 'sta', 'ste', 'stran', 'stvar', 'sva', 't', 'ta', 'tak', 'taka', 'take', 'taki', 'tako', 'takoj', 'tam', 'te', 'tebe', 'tebi', 'tega', 'težak', 'težka', 'težki', 'težko', 'ti', 'tista', 'tiste', 'tisti', 'tisto', 'tj.', 'tja', 'to', 'toda', 'torek', 'tretja', 'tretje', 'tretji', 'tri', 'tu', 'tudi', 'tukaj', 'tvoj', 'tvoja', 'tvoje', 'u', 'v', 'vaju', 'vam', 'vas', 'vaš', 'vaša', 'vaše', 've', 'vedno', 'velik', 'velika', 'veliki', 'veliko', 'vendar', 'ves', 'več', 'vi', 'vidva', 'vii', 'viii', 'visok', 'visoka', 'visoke', 'visoki', 'vsa', 'vsaj', 'vsak', 'vsaka', 'vsakdo', 'vsake', 'vsaki', 'vsakomur', 'vse', 'vsega', 'vsi', 'vso', 'včasih', 'včeraj', 'x', 'z', 'za', 'zadaj', 'zadnji', 'zakaj', 'zaprta', 'zaprti', 'zaprto', 'zdaj', 'zelo', 'zunaj', 'č', 'če', 'često', 'četrta', 'četrtek', 'četrti', 'četrto', 'čez', 'čigav', 'š', 'šest', 'šesta', 'šesti', 'šesto', 'štiri', 'ž', 'že']
slovenian_stopwords += ['še', 'tko']

def get_stopwords(lang):
    if lang != 'sl':
        raise NotImplemented('Only slovenian stopwords are currently supported.')
    
    return slovenian_stopwords

def get_dates_between(datetime_from=datetime.now(), datetime_to=datetime.now()):
    number_of_days = (datetime_to - datetime_from).days

    return [(datetime_from + timedelta(days=i)) for i in range(number_of_days)]

def get_fortnights_between(datetime_from=datetime.now(), datetime_to=datetime.now()):
    number_of_fortnights = (datetime_to - datetime_from).days % 14

    return [(datetime_from + timedelta(days=(i * 14))) for i in range(number_of_fortnights)]

def remove_punctuation(text):
    return text.translate(str.maketrans('', '', punctuation))

def tokenize(text):
    return [s for s in text.split(' ') if s != '']


# TODO lemmatization only works for slovenian
# initialize the lemmatizer class only once
lemmatiser = Lemmatiser()
def lemmatize(token):
    return lemmatiser.lemmatise_token(token)[0][1]

def lemmatize_many(tokens):
    return [x[1] for x in lemmatiser.tag_lemmatise_sent(tokens)]
