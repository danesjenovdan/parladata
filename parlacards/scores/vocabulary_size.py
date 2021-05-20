from collections import Counter
from datetime import datetime
from string import punctuation

from parladata.models.person import Person
from parladata.models.speech import Speech

from parlacards.models import PersonVocabularySize

from parlacards.scores.common import get_dates_between, get_fortnights_between

def remove_punctuation(text):
    return text.translate(str.maketrans('', '', punctuation))

def tokenize(text):
    return [s for s in text.split(' ') if s != '']

def calculate_vocabulary_size(speeches):
    # if there are no speeches return 0
    if speeches.count() == 0:
        return 0

    word_counter = Counter()

    for speech in speeches:
        for token in tokenize(remove_punctuation(speech.strip().lower())):
            word_counter[token] += 1
    
    number_of_unique_words = len(word_counter.keys())

    frequency_counter = Counter()

    for frequency in word_counter.values():
        frequency_counter[str(frequency)] += 1

    return number_of_unique_words / (
        sum([(
            frequency_counter[frequency] + (int(frequency) ** 2)
        ) for frequency in frequency_counter.keys()])
    )

def save_vocabulary_size(person, playing_field, timestamp=datetime.now()):
    # TODO maybe get valid speeches
    # get speeches that started before the timestamp
    speeches = Speech.objects.filter(
        speaker=person,
        start_time__lte=timestamp
    ).values_list('content', flat=True)

    PersonVocabularySize(
        person=person,
        value=calculate_vocabulary_size(speeches),
        timestamp=timestamp,
        playing_field=playing_field,
    ).save()

def save_all_vocabulary_sizes_at(playing_field, timestamp=datetime.now()):
    people = playing_field.query_voters(timestamp)

    for person in people:
        save_vocabulary_size(person, playing_field, timestamp)

def save_all_vocabulary_sizes_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_dates_between(datetime_from, datetime_to):
        save_all_vocabulary_sizes_at(playing_field, timestamp=day)

def save_sparse_vocabulary_sizes_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_fortnights_between(datetime_from, datetime_to):
        save_all_vocabulary_sizes_at(playing_field, timestamp=day)
