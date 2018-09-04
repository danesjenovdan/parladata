# -*- coding: utf-8 -*-
import csv
from parladata.models import Speech, Person, Membership, Organization, Post, Session
from datetime import datetime
from difflib import unified_diff
from django.db.models import Q
from django.conf import settings

from sandbox.tokeniser.tokeniser import generate_tokenizer, process

import editdistance


roles = ['president',
         'deputy']

class Tokeniser:
    """
    Tokeniser wrapper class.
    Use tokenise(self, txt) for full result.
    Use only_tokens(self, processed) with output from tokenise(self, txt) to only get tokens.
    Use represent_from_tokeniser(self, processed) with output from tokenise(self, txt) to inspect/debug output.
    """

    def __init__(self):
        print('Tokeniser initialised.')

    def represent_from_tokeniser(self, processed):
        for sentence in processed:
            for token, start, end in sentence:
                if not token[0].isspace():
                    print(token)

    def test_me(self):
        tokenizer = generate_tokenizer('sl')
        represent_from_tokeniser(process['standard'](tokenizer, test_text, 'sl'))

    def tokenise(self, txt):
        tokenizer = generate_tokenizer('sl')
        return process['standard'](tokenizer, txt, 'sl')

    def only_tokens(self, processed):
        output = []

        for sentence in processed:
            for token, start, end in sentence:
                if not token[0].isspace():
                    output.append(token)
        
        return output

tokeniser = Tokeniser()

def count_versions():
    parties = Organization.objects.filter(classification__in=settings.settings.PS_NP)
    mems = Membership.objects.filter(organization__in=parties)
    people = [mem.person_id for mem in mems.distinct('person')]
    speeches = Speech.getValidSpeeches(datetime.now())
    counts = {}
    items = speeches.count()
    visited = 0
    dates = []
    for speech in speeches:
        visited += 1
        versions = get_version_of_speech_distinct_count(speech)
        counts[str(speech.id)] = versions
        if versions > 1:
            dates.append(speech.create)

        if visited % 100 == 0:
            printProgressBar(iteration=visited, total=items)
    print min(dates), max(dates)
    return counts

def get_version_of_speech(speech):
    if speech.version_con:
        versions = Speech.objects.filter(version_con=speech.version_con,
                                         start_time=speech.start_time,
                                         speaker_id=speech.speaker_id,
                                         session_id=speech.session_id)
        return versions.distinct('content').distinct('created_at').order_by('created_at')
    return Speech.objects.filter(id=speech.id)


def get_version_of_speech_levenshtein(speech):
    versions = Speech.objects.filter(#order__in=range(speech.order - 2, speech.order + 3),
                                     start_time=speech.start_time,
                                     speaker_id=speech.speaker_id,
                                     session_id=speech.session_id)
    versions = exclude_non_equal_speeches(versions, speech)
    return versions


def get_version_of_speech_distinct_count(speech):
    versions = get_version_of_speech(speech).count()
    return versions

def get_diffs_of_speech(speech):
    versions = get_version_of_speech(speech)
    for i in range(len(versions) - 1):
        for i in unified_diff(tokeniser.only_tokens(tokeniser.tokenise(versions[i].content)), tokeniser.only_tokens(tokeniser.tokenise(versions[i+1].content))):
            if ('+' or '-') in i:
                print i

    return versions


def get_word_count_in_diffs_of_speech(speech, word, blacklist=[]):
    count = 0
    versions = get_version_of_speech(speech)
    for i in range(len(versions) - 1):
        for i in unified_diff(tokeniser.only_tokens(tokeniser.tokenise(versions[i].content)), tokeniser.only_tokens(tokeniser.tokenise(versions[i+1].content))):
            if len(i)>0:
                if i[1:].lower() in blacklist:
                    continue
            if ('+' in i) or ('-' in i):
                if not '@' in i:
                    if word in i or word == '*':
                        count += 1
                        print i

    return count


def get_plus_minus_of_speech_diff(speech, blacklist=[]):
    versions = get_version_of_speech(speech)
    out = []
    for i in range(len(versions) - 1):
        count = 0
        for j in unified_diff(tokeniser.only_tokens(tokeniser.tokenise(versions[i].content)), tokeniser.only_tokens(tokeniser.tokenise(versions[i+1].content))):
            if len(j)>0:
                if j[1:].lower() in blacklist:
                    continue
                if (j[1:3] == '++') or (j[1:3] == '--'):
                    continue
                if j[0] == '+':
                    print "plus", j
                    count += 1
                elif j[0] == '-':
                    print "minust", j
                    count -= 1
        out.append({'cmp_speeches': str(versions[i].id) + ' : ' + str(versions[i+1].id),
                    'plus-minus': count})
    return out


def get_count_of_added_removed_words_speech(speech, word, start_with='+', blacklist=[]):
    count = 0
    versions = get_version_of_speech(speech)
    for i in range(len(versions) - 1):
        for i in unified_diff(tokeniser.only_tokens(tokeniser.tokenise(versions[i].content)), tokeniser.only_tokens(tokeniser.tokenise(versions[i+1].content))):
            if len(i)>0:
                if i[1:].lower() in blacklist:
                    continue
            if word in i or word == '*':
                if i[0] == start_with:
                    count += 1
                    print i   

    return count


#count = words/chars
def get_count_of_changes_longer_then(speech, length, count='words', blacklist=[]):
    def append_(condition, word):
        if condition == 'words':
            return 1
        else:
            return len(word)
    output = []
    versions = get_version_of_speech(speech)

    current_length = 0
    current_words = []
    for i in range(len(versions) - 1):
        for i in unified_diff(tokeniser.only_tokens(tokeniser.tokenise(versions[i].content)), tokeniser.only_tokens(tokeniser.tokenise(versions[i+1].content))):
            if len(i)>0:
                if i[1:].lower() in blacklist:
                    continue
                if i[0] in ['+', '-']:
                    current_words.append(i)
                    current_length += append_(count, i)
                else:
                    if current_length > length:
                        output.append(' '.join(current_words))
                        current_words = []
                        current_length = 0
                    else:
                        current_words = []
                        current_length = 0
            else:
                current_words = []
                current_length = 0


    return output

# spremembe dalše od n znakov. spemembe dalše od n besed, beseda je dalša od, exlude query

def get_words_which_is_longer_than(speech, length, blacklist=[]):
    def append_(condition, word):
        if condition == 'words':
            return 1
        else:
            return len(word)
    output = []
    versions = get_version_of_speech(speech)

    for i in range(len(versions) - 1):
        for i in unified_diff(tokeniser.only_tokens(tokeniser.tokenise(versions[i].content)), tokeniser.only_tokens(tokeniser.tokenise(versions[i+1].content))):
            if len(i)>0:
                if i[1:].lower() in blacklist:
                    continue
                if i[0] in ['+', '-']:
                    if len(i[1:]) > length:
                        output.append(i)
    return output


def printProgressBar(iteration,
                     total,
                     prefix='',
                     suffix='',
                     decimals=1,
                     length=100,
                     fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r' + prefix + '|' + bar + '|' + percent + suffix + '\r'),
    # Print New Line on Complete
    if iteration == total:
        print()



"""
usage
speechez=Speech.getValidSpeeches(datetime.now()).order_by("-created_at")[:500]
data=run_speeches_on_method(speechez, get_count_of_changes_longer_then, length=6, count='words')
"""
def run_speeches_on_method(speeches, method, **kwargs):
    output = {}
    f = open('changes_words.txt', 'w')
    items = speeches.count()
    visited = 0
    for speech in speeches:
        visited += 1
        if get_version_of_speech_distinct_count(speech) > 1:
            data = method(speech, **kwargs)
            f.write(str(speech.id) + ': ' + str(data) + '\n')
        if visited % 100 == 0:
            printProgressBar(iteration=visited, total=items)
    f.close()
    return output


def get_():
    counts = count_versions()
    speech_ids = ([i if j>1 else None for i, j in counts.items()])
    while None in speech_ids:
        speech_ids.remove(None)

    speeches = Speech.objects.filter(id__in=speech_ids)

    all_speeches = Speech.getValidSpeeches(datetime.now())

    partys = Counter(speeches.values_list('party___name', flat=True))
    orgs = Counter(speeches.values_list('session__organization___name', flat=True))

    partys_all = Counter(all_speeches.values_list('party___name', flat=True))
    orgs_all = Counter(all_speeches.values_list('session__organization___name', flat=True))



def count_versions():
    parties = Organization.objects.filter(classification__in=settings.PS_NP)
    mems = Membership.objects.filter(organization__in=parties)
    people = [mem.person_id for mem in mems.distinct('person')]
    speeches = Speech.getValidSpeeches(datetime.now())
    counts = {}
    items = speeches.count()
    visited = 0
    dates = []
    for speech in speeches:
        visited += 1
        versions = get_version_of_speech(speech)
        if versions.count() > 1:
            dates.append(versions.earliest('updated_at').updated_at)

        if visited % 100 == 0:
            print 'trenutno je povprecno: ' + str(float(sum(counts.values()))/visited) + ' verzij na govor'
            printProgressBar(iteration=visited, total=items)
    print min(dates), max(dates)
    return counts


def is_equal_content(i, j):
    max_len = max([len(i), len(j)])
    dist = editdistance.eval(i, j)
    if max_len == 0:
        return True
    diff = float(dist) / max_len
    if diff > 0.25:
        return False
    else:
        return True


def exclude_non_equal_speeches(versions, orginal):
    for version in versions:
        if not is_equal_content(version.content, orginal.content):
            versions = versions.exclude(id=version.id)
    return versions


# set version_con to speeches
def fix_session_version_con(session_id):
    i=0
    session = Session.objects.get(id=session_id)
    memberships = session.organization.memberships.all()
    val_speeches = Speech.getValidSpeeches(datetime.now()).filter(session_id=session_id)
    all_speeches = Speech.objects.filter(session_id=session_id)

    posts = Post.objects.filter(membership__in=memberships, role__in=roles)
    fdate = session.start_time
    posts = posts.filter(Q(start_time__lte=fdate) |
                         Q(start_time=None),
                         Q(end_time__gte=fdate) |
                         Q(end_time=None))
    leaders = posts.values_list('membership__person_id', flat=True)

    if val_speeches.count() == all_speeches.count():
        print 'Session ' + str(session_id) + 'has no version'
        return
    for speech in val_speeches:
        print i
        if speech.speaker_id in leaders:
            continue
        versions = get_version_of_speech_levenshtein(speech)
        versions.update(version_con=i)
        i += 1


