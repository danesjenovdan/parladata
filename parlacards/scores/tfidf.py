from django.db.models import Q
from datetime import datetime
from parladata.models.session import Session

from sklearn.feature_extraction.text import TfidfVectorizer

from parladata.models.speech import Speech
from parladata.models.memberships import PersonMembership

from parlacards.models import PersonTfidf, GroupTfidf, SessionTfidf

from parlacards.scores.common import (
    get_lemmatize_method,
    get_dates_between,
    get_fortnights_between
)

#
# PERSON
#
def calculate_people_tfidf(playing_field, timestamp=datetime.now()):
    # TODO we should probably avoid casting
    # competitor_ids and leader_ids into list
    competitor_ids = list(
        playing_field.query_voters(
            timestamp
        ).order_by(
            'id'
        ).values_list(
            'id',
            flat=True
        )
    )

    # if a leader exists he should be a competitor as well
    # TODO this is a very broad filter, it will probably
    # need to be reworked into something more precise
    leader_ids = list(
        PersonMembership.objects.filter(
            role='leader'
        ).order_by(
            'id'
        ).values_list(
            'member__id',
            flat=True
        )
    )
    # add leader ids to competitor ids
    competitor_ids += leader_ids
    # and sort in place
    competitor_ids.sort()

    playing_field_speeches = Speech.objects.filter_valid_speeches(
        timestamp
    ).filter(
        Q(start_time__lte=timestamp) | Q(start_time__isnull=True),
        speaker__id__in=competitor_ids,
        lemmatized_content__isnull=False
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
    get_stopwords = get_lemmatize_method("get_stopwords")
    tfidfVectorizer = TfidfVectorizer(
        lowercase=False, # do not transform to lowercase
        preprocessor=lambda x: x, # do not preprocess
        tokenizer=lambda x: x.split(' '), # tokenize by splitting at ' '
        stop_words=get_stopwords(),
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
            'tfidf': competitor_tfidf[:30]
        })

    return output

def save_people_tfidf(playing_field, timestamp=datetime.now()):
    people_tfidf = calculate_people_tfidf(playing_field, timestamp)

    for tfidf in people_tfidf:
        for score in tfidf['tfidf']:
            if score[1] > 0 and score[0] != '':
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

#
# GROUP
#
def calculate_groups_tfidf(playing_field, timestamp=datetime.now()):
    # TODO this is very similar to calculate_people_tfidf
    # consider refactoring
    groups = playing_field.query_organization_members(
        timestamp
    ).order_by(
        'id'
    )

    group_speeches = [
        ' '.join(
            Speech.objects.filter_valid_speeches(
                timestamp
            ).filter(
                Q(start_time__lte=timestamp) | Q(start_time__isnull=True),
                speaker__id__in=group.query_members(timestamp).values('id'),
                lemmatized_content__isnull=False,
            ).values_list(
                'lemmatized_content',
                flat=True
            )
        ) for group in groups
    ]
    get_stopwords = get_lemmatize_method("get_stopwords")
    tfidfVectorizer = TfidfVectorizer(
        lowercase=False, # do not transform to lowercase
        preprocessor=lambda x: x, # do not preprocess
        tokenizer=lambda x: x.split(' '), # tokenize by splitting at ' '
        stop_words=get_stopwords(),
        use_idf=True
    )

    tfidf = tfidfVectorizer.fit_transform(group_speeches)

    feature_names = tfidfVectorizer.get_feature_names()

    output = []
    for group_index, group_id in enumerate(groups.values_list('id', flat=True)):
        group_tfidf = [
            (
                feature_names[feature_index],
                float(value)
            ) for feature_index, value in enumerate(
                tfidf[group_index].T.todense()
            )
        ]
        # sort in place
        group_tfidf.sort(key=lambda x: x[1], reverse=True)

        # TODO when refactoring change this to a single
        # dictionary instead of a list of dictionaries
        output.append({
            'group_id': group_id,
            'tfidf': group_tfidf[:30]
        })

    return output

def save_groups_tfidf(playing_field, timestamp=datetime.now()):
    groups_tfidf = calculate_groups_tfidf(playing_field, timestamp)

    for tfidf in groups_tfidf:
        for score in tfidf['tfidf']:
            if score[1] > 0 and score[0] != '':
                GroupTfidf(
                    group_id=tfidf['group_id'],
                    timestamp=timestamp,
                    token=score[0],
                    value=score[1],
                    playing_field=playing_field
                ).save()

def save_groups_tfidf_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_dates_between(datetime_from, datetime_to):
        save_groups_tfidf(playing_field, timestamp=day)

def save_sparse_groups_tfidf_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_fortnights_between(datetime_from, datetime_to):
        save_groups_tfidf(playing_field, timestamp=day)

#
# SESSION
#
def calculate_sessions_tfidf(playing_field, timestamp=datetime.now()):
    # TODO this is very similar to calculate_people_tfidf
    # consider refactoring
    session_ids = Session.objects.filter(
        organizations=playing_field,
        start_time__lte=timestamp
    ).order_by('id').values_list('id', flat=True)

    playing_field_speeches = Speech.objects.filter_valid_speeches(
        timestamp
    ).filter(
        Q(start_time__lte=timestamp) | Q(start_time__isnull=True),
        session__id__in=session_ids,
        lemmatized_content__isnull=False,
    )

    all_speeches = [
        ' '.join(
            playing_field_speeches.filter(
                session__id=session_id
            ).values_list(
                'lemmatized_content',
                flat=True
            )
        ) for session_id in session_ids
    ]

    get_stopwords = get_lemmatize_method("get_stopwords")
    tfidfVectorizer = TfidfVectorizer(
        lowercase=False, # do not transform to lowercase
        preprocessor=lambda x: x, # do not preprocess
        tokenizer=lambda x: x.split(' '), # tokenize by splitting at ' '
        stop_words=get_stopwords(),
        use_idf=True
    )

    tfidf = tfidfVectorizer.fit_transform(all_speeches)

    feature_names = tfidfVectorizer.get_feature_names()

    output = []
    for session_index, session_id in enumerate(session_ids):
        session_tfidf = [
            (
                feature_names[feature_index],
                float(value)
            ) for feature_index, value in enumerate(
                tfidf[session_index].T.todense()
            )
        ]
        # sort in place
        session_tfidf.sort(key=lambda x: x[1], reverse=True)

        # TODO when refactoring change this to a single
        # dictionary instead of a list of dictionaries
        output.append({
            'session_id': session_id,
            'tfidf': session_tfidf[:30]
        })

    return output

def save_sessions_tfidf(playing_field, timestamp=datetime.now()):
    sessions_tfidf = calculate_sessions_tfidf(playing_field, timestamp)

    for tfidf in sessions_tfidf:
        for score in tfidf['tfidf']:
            if score[1] > 0 and score[0] != '':
                SessionTfidf(
                    session_id=tfidf['session_id'],
                    timestamp=timestamp,
                    token=score[0],
                    value=score[1],
                    playing_field=playing_field
                ).save()

def save_sessions_tfidf_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_dates_between(datetime_from, datetime_to):
        save_sessions_tfidf(playing_field, timestamp=day)

def save_sparse_sessions_tfidf_between(playing_field, datetime_from=datetime.now(), datetime_to=datetime.now()):
    for day in get_fortnights_between(datetime_from, datetime_to):
        save_sessions_tfidf(playing_field, timestamp=day)

def save_session_tfidf_on_last_speech_date(playing_field, session):
    timestamp = session.speeches.latest('start_time').start_time
    sessions_tfidf = calculate_sessions_tfidf(playing_field, timestamp)

    for tfidf in sessions_tfidf:
        for score in tfidf['tfidf']:
            if tfidf['session_id'] == session.id and score[1] > 0 and score[0] != '':
                SessionTfidf(
                    session_id=tfidf['session_id'],
                    timestamp=timestamp,
                    token=score[0],
                    value=score[1],
                    playing_field=playing_field
                ).save()

def save_sessions_tfidf_on_last_speech_date(playing_field, sessions):
    timestamp = datetime.now()
    sessions_tfidf = calculate_sessions_tfidf(playing_field, timestamp)
    session_ids = sessions.values_list('id', flat=True)

    for tfidf in sessions_tfidf:
        for score in tfidf['tfidf']:
            if tfidf['session_id'] in session_ids and score[1] > 0 and score[0] != '':
                SessionTfidf(
                    session_id=tfidf['session_id'],
                    timestamp=timestamp,
                    token=score[0],
                    value=score[1],
                    playing_field=playing_field
                ).save()

def save_sessions_tfidf_for_fresh_sessions(playing_field):
    sessions = Session.objects.filter(
        speeches__isnull=False,
        sessiontfidf_related__isnull=True
    ).distinct('id')

    save_sessions_tfidf_on_last_speech_date(playing_field, sessions)
