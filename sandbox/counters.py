from parladata.models import Organization, Speech, Membership
from django.db.models import Q
import lemmagen.lemmatizer
from lemmagen.lemmatizer import Lemmatizer
from nltk.tokenize import word_tokenize
from string import punctuation
from collections import Counter
from datetime import datetime


def getSpeechesOfPGs(from_year, is_coalition=None):
    pos = ['poslanska skupina', 'nepovezani poslanec']
    parlGroups = Organization.objects.filter(classification__in=pos)
    if is_coalition is not None:
        parlGroups = parlGroups.filter(is_coalition=is_coalition)
    speechesByGroup = {}
    start_time = datetime(day=1,
                          month=1,
                          year=from_year)
    if is_coalition is None:
        for group in parlGroups:
            speeches = Speech.objects.filter(party__id=group.id,
                                             start_time__lte=start_time)
            speechesByGroup[group.id] = speeches

        return speechesByGroup
    else:
        groups = parlGroups.values_list("id", flat=True)
        print "Groups in ", groups
        return {0: Speech.objects.filter(party__id__in=groups,
                                         start_time__lte=start_time)}


def getSpeechesOfMembers(from_year):
    mems = getMembers()
    speechesByMember = {}
    start_time = datetime(day=1,
                          month=1,
                          year=from_year)
    for member in mems:
        speeches = Speech.objects.filter(speaker__id=member.id,
                                         start_time__lte=start_time)
        speechesByMember[member.id] = speeches
    return speechesByMember


# Key of retuned objects is 0
def getSpeechesOfCoal(from_year):
    return getSpeechesOfPGs(from_year, is_coalition=1)


# Key of retuned objects is 0
def getSpeechesOfOppo(from_year):
    return getSpeechesOfPGs(from_year, is_coalition=-1)


def lemmatizeTokens(tokens):

    lemmatized_tokens = []
    lemmatizer = Lemmatizer(dictionary=lemmagen.DICTIONARY_SLOVENE)

    for token in tokens:
        lemmatized_tokens.append(lemmatizer.lemmatize(token))

    return lemmatized_tokens


def counterOfUniqueWords(speechesQS):
    out = {}
    for owner, speeches in speechesQS.items():
        print "Stejem: ", owner
        out[owner] = getWordsCounter(''.join(speeches.values_list('content',
                                                                  flat=True)))
    return out


def getWordsCounter(text):
    exclude = set(punctuation)
    text_lower = text.lower()
    text_nopunct_lower = ''.join(ch for ch in text_lower if ch not in exclude)
    tokens = lemmatizeTokens(word_tokenize(text_nopunct_lower))
    new_count = Counter(tokens)
    return new_count


def getMembers():
    pos = ['poslanska skupina', 'nepovezani poslanec']
    parliamentaryGroups = Organization.objects.filter(classification__in=pos)
    mems = Membership.objects.filter(Q(start_time__lte=datetime.now()) |
                                     Q(start_time=None),
                                     Q(end_time__gte=datetime.now()) |
                                     Q(end_time=None),
                                     organization__in=parliamentaryGroups)
    return mems


def getSurenames():
    mems = getMembers()
    surenames = mems.values_list("person__family_name", flat=True)
    out = lemmatizeTokens([surename.split(" ")[0].lower() for surename in surenames])
    return out
