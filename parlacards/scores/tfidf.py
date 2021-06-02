from datetime import datetime

from sklearn.feature_extraction.text import TfidfVectorizer

from parladata.models.speech import Speech

from parlacards.models import PersonTfidf

from parlacards.scores.common import (
    get_stopwords,
    get_dates_between,
    get_fortnights_between
)

def calculate_people_tfidf(playing_field, timestamp=datetime.now()):
    competitor_ids = playing_field.query_voters(
        timestamp
    ).order_by(
        'id'
    ).values_list(
        'id',
        flat=True
    )

    playing_field_speeches = Speech.objects.filter_valid_speeches(
        timestamp
    ).filter(
        speaker__id__in=competitor_ids,
        start_time__lte=timestamp
    )

    all_speeches = [
        ' '.join(
            playing_field_speeches.filter(
                speaker__id=competitor_id
            ).values_list(
                'lemmatized_content',
                flat=True
            )
        ) for competitor_id in competitor_ids
    ]

    tfidfVectorizer = TfidfVectorizer(
        lowercase=False, # do not transform to lowercase
        preprocessor=lambda x: x, # do not preprocess
        tokenizer=lambda x: x.split(' '), # tokenize by splitting at ' '
        stop_words=get_stopwords('sl'),
        use_idf=True
    )

    tfidf = tfidfVectorizer.fit_transform(all_speeches)

    feature_names = tfidfVectorizer.get_feature_names()

    output = []
    for competitor_index, competitor_id in enumerate(competitor_ids):
        competitor_tfidf = [
            (
                feature_names[feature_index],
                float(value)
            ) for feature_index, value in enumerate(
                tfidf[competitor_index].T.todense()
            )
        ]
        # sort in place
        competitor_tfidf.sort(key=lambda x: x[1], reverse=True)

        output.append({
            'speaker_id': competitor_id,
            'tfidf': competitor_tfidf[:20]
        })

    return output

def save_people_tfidf(playing_field, timestamp=datetime.now()):
    people_tfidf = calculate_people_tfidf(playing_field, timestamp)

    for tfidf in people_tfidf:
        for score in tfidf['tfidf']:
            PersonTfidf(
                person_id=tfidf['speaker_id'],
                timestamp=timestamp,
                token=score[0],
                value=score[1],
                playing_field=playing_field
            ).save()

def save_people_tfidf_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_dates_between(datetime_from, datetime_to):
        save_people_tfidf(playing_field, timestamp=day)

def save_sparse_people_tfidf_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_fortnights_between(datetime_from, datetime_to):
        save_people_tfidf(playing_field, timestamp=day)
