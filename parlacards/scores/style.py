from collections import Counter

from parlacards.scores.common import (
    get_dates_between,
    get_fortnights_between,
    remove_punctuation,
    tokenize,
    lemmatize
)

def get_styled_lemmas(style):
    # TODO current work directory?
    with open(f'parlacards/scores/styled_lemmas/{style}.csv', 'r') as infile:
        return [line.strip() for line in infile.readlines()]

def calculate_style_score(speeches, styled_lemmas):
    # if there are no speeches return 0
    if speeches.count() == 0:
        return 0

    word_counter = Counter()
    styled_words_counter = Counter()

    for speech in speeches:
        # TODO what if there is no lemmatized_content
        if not speech:
            raise ValueError('Lemmatized speech is missing.')
        for token in lemmatize(tokenize(remove_punctuation(speech.strip().lower()))):
            word_counter[token] += 1
            if token in styled_lemmas:
                styled_words_counter[token] += 1

    # return percentage of styled words
    return len(styled_words_counter.keys()) / len(word_counter.keys()) * 100

def save_person_style_scores(person, playing_field, timestamp=datetime.now()):
    # get speeches that started before the timestamp
    speeches = Speech.objects.filter_valid_speeches(timestamp).filter(
        speaker=person,
        start_time__lte=timestamp
    ).values_list('lemmatized_content', flat=True)
    # TODO what if there is no lemmatized content

    for style in ['problematic', 'simple', 'sophisticated']:
        PersonStyleScore(
            person=person,
            value=calculate_style_score(speeches, get_styled_lemmas(style)),
            style=style,
            timestamp=timestamp,
            playing_field=playing_field,
        ).save()

def save_people_style_scores(playing_field, timestamp=datetime.now()):
    people = playing_field.query_voters(timestamp)

    for person in people:
        save_person_style_scores(person, playing_field, timestamp)

def save_people_style_scores_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_dates_between(datetime_from, datetime_to):
        save_people_style_scores(playing_field, timestamp=day)

def save_sparse_people_style_scores_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_fortnights_between(datetime_from, datetime_to):
        save_people_style_scores(playing_field, timestamp=day)
