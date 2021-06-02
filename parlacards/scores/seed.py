from datetime import datetime, timedelta

from parladata.models.organization import Organization

from parlacards.scores.vocabulary_size import (
    save_sparse_people_vocabulary_sizes_between,
    save_sparse_groups_vocabulary_sizes_between
)
from parlacards.scores.voting_distance import save_sparse_voting_distances_between
from parlacards.scores.deviation_from_group import save_sparse_people_deviations_from_group_between
from parlacards.scores.avg_number_of_speeches_per_session import save_sparse_people_avg_number_of_speeches_per_session_between
from parlacards.scores.number_of_questions import save_sparse_people_number_of_questions_between
from parlacards.scores.attendance import save_sparse_people_vote_attendance_between
from parlacards.scores.monthly_attendance import (
    save_sparse_people_monthly_vote_attendance_between,
    save_sparse_groups_monthly_vote_attendance_between
)
from parlacards.scores.style import save_sparse_people_style_scores_between
from parlacards.scores.number_of_spoken_words import save_sparse_people_number_of_spoken_words_between

def calculate_sparse_scores(playing_field):
    datetime_to = datetime.now()
    datetime_from = datetime_to - timedelta(days=100)

    print('Calculating people vocabulary sizes ...')
    save_sparse_people_vocabulary_sizes_between(playing_field, datetime_from, datetime_to)
    print('Calculating organization vocabulary sizes ...')
    save_sparse_groups_vocabulary_sizes_between(playing_field, datetime_from, datetime_to)
    print('Calculating voting distances ...')
    save_sparse_voting_distances_between(playing_field, datetime_from, datetime_to)
    print('Calculating deviations from group ...')
    save_sparse_people_deviations_from_group_between(playing_field, datetime_from, datetime_to)
    print('Calculating average number of speeches ...')
    save_sparse_people_avg_number_of_speeches_per_session_between(playing_field, datetime_from, datetime_to)
    print('Calculating number of questions ...')
    save_sparse_people_number_of_questions_between(playing_field, datetime_from, datetime_to)
    print('Calculating vote attendance ...')
    save_sparse_people_vote_attendance_between(playing_field, datetime_from, datetime_to)
    print('Calculating monthly vote attendance ...')
    save_sparse_people_monthly_vote_attendance_between(playing_field, datetime_from, datetime_to)
    print('Calculating monthly vote attendance ...')
    save_sparse_groups_monthly_vote_attendance_between(playing_field, datetime_from, datetime_to)
    print('Calculating style scores ...')
    save_sparse_people_style_scores_between(playing_field, datetime_from, datetime_to)
    print('Calculating number of spoken words ...')
    save_sparse_people_number_of_spoken_words_between(playing_field, datetime_from, datetime_to)
    print('Done.')
