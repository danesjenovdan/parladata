# -*- coding: utf-8 -*-
from parladata.models import Organization, Speech, PersonMembership, Session, Vote, Ballot
from django.db.models import Q
import lemmagen.lemmatizer
from lemmagen.lemmatizer import Lemmatizer
from nltk.tokenize import word_tokenize
from string import punctuation
from collections import Counter
from datetime import datetime
from slugify import slugify
import requests
from django.http import JsonResponse

from sandbox.export import listToCSV


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
        print("Groups in ", groups)
        return {0: Speech.objects.filter(party__id__in=groups,
                                         start_time__lte=start_time)}


def getSpeechesOfMembers(from_year):
    mems = getMembers()
    speechesByMember = {}
    start_time = datetime(day=1,
                          month=1,
                          year=from_year)
    for member in mems:
        speeches = Speech.objects.filter(speaker__id=member.person.id,
                                         start_time__lte=start_time)
        speechesByMember[member.person.id] = speeches
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
    for owner, speeches in list(speechesQS.items()):
        print("Stejem: ", owner)
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
    mems = PersonMembership.objects.filter(Q(start_time__lte=datetime.now()) |
                                     Q(start_time=None),
                                     Q(end_time__gte=datetime.now()) |
                                     Q(end_time=None),
                                     organization__in=parliamentaryGroups)
    return mems


def getSurenames():
    mems = getMembers()
    surenames = mems.values_list("person__family_name", flat=True)
    lowerNames = [surename.split(" ")[0].lower() for surename in surenames]
    out = lemmatizeTokens(lowerNames)
    return out, {lem: org for lem, org in zip(out, lowerNames)}


def getTopWordsOf(typeOf='pg', nWords=1000, from_year=2016):
    all_keys = {}
    if typeOf == 'pg':
        gS = getSpeechesOfPGs(from_year)
        p_data = requests.get('https://data.parlameter.si/v1/getAllPGs').json()
        all_keys = {str(obj['id']): obj['acronym'] for obj in list(p_data.values())}
    else:
        gS = getSpeechesOfMembers(from_year)
        p_data = requests.get('https://data.parlameter.si/v1/getMPs').json()
        all_keys = {str(obj['id']): obj['name'] for obj in p_data}

    print(all_keys)
    cP = counterOfUniqueWords(gS)
    for key in list(cP.keys()):
        if str(key) in list(all_keys.keys()):
            file_name = slugify(all_keys[str(key)]) + '_top' + str(nWords) + '.csv'
        else:
            file_name = str(key) + '_top' + str(nWords) + '.csv'
        listToCSV([("Beseda", "Števec")]+cP[key].most_common(nWords), file_name)


def getCountOfMentionedOthers(typeOf='pg', from_year=2016):
    lemNames, pairs = getSurenames()
    all_keys = {}
    if typeOf == 'pg':
        gS = getSpeechesOfPGs(from_year)
        p_data = requests.get('https://data.parlameter.si/v1/getAllPGs').json()
        all_keys = {str(obj['id']): obj['acronym'] for obj in list(p_data.values())}
    else:
        gS = getSpeechesOfMembers(from_year)
        p_data = requests.get('https://data.parlameter.si/v1/getMPs').json()
        all_keys = {str(obj['id']): obj['name'] for obj in p_data}

    print(all_keys)
    cP = counterOfUniqueWords(gS)
    for key in list(cP.keys()):
        if str(key) in list(all_keys.keys()):
            file_name = slugify(all_keys[str(key)]) + '_mentioned' + '.csv'
        else:
            file_name = str(key) + '_mentioned' + '.csv'
        data = [["Priimek", "Števec"]]+[[pairs[lem], cP[key][lem]] for lem in lemNames]
        listToCSV(data, file_name)


def getPresence(request):
    ses = Session.objects.filter(organization_id=95)
    presence = []
    for s in ses:
        votes = s.vote_set.all()
        sesData = {}
        for v in votes:
            sesData[str(v.id)] = list(v.ballots.exclude(option='ni').values_list('voter_id', flat=True))
            print(len(sesData[str(v.id)]))
        sesData['on_session'] = list(set(sum(list(sesData.values()), [])))
        print('on session', len(sesData['on_session']))
        sesData['name'] = s.name
        presence.append(sesData)
    return JsonResponse(presence, safe=False)
