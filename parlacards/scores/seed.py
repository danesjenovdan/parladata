from datetime import datetime, timedelta

from parladata.models.organization import Organization

from parlacards.scores.vocabulary_size import (
    save_sparse_people_vocabulary_sizes_between,
    save_sparse_organizations_vocabulary_sizes_between
)
from parlacards.scores.voting_distance import save_sparse_voting_distances_between
from parlacards.scores.deviation_from_group import save_sparse_people_deviations_from_group_between
from parlacards.scores.avg_number_of_speeches_per_session import save_sparse_people_avg_number_of_speeches_per_session_between
from parlacards.scores.number_of_questions import save_sparse_people_number_of_questions_between
from parlacards.scores.presence import save_sparse_people_presence_on_votes_between
from parlacards.scores.monthly_presence import save_people_monthly_presence_on_votes

def calculate_sparse_scores(playing_field):
    datetime_to = datetime.now()
    datetime_from = datetime_to - timedelta(days=100)

    print('Calculating people vocabulary sizes ...')
    save_sparse_people_vocabulary_sizes_between(playing_field, datetime_from, datetime_to)
    print('Calculating organization vocabulary sizes ...')
    save_sparse_organizations_vocabulary_sizes_between(playing_field, datetime_from, datetime_to)
    print('Calculating voting distances ...')
    save_sparse_voting_distances_between(playing_field, datetime_from, datetime_to)
    print('Calculating deviations from group ...')
    save_sparse_people_deviations_from_group_between(playing_field, datetime_from, datetime_to)
    print('Calculating average number of speeches ...')
    save_sparse_people_avg_number_of_speeches_per_session_between(playing_field, datetime_from, datetime_to)
    print('Calculating number of questions ...')
    save_sparse_people_number_of_questions_between(playing_field, datetime_from, datetime_to)
    print('Calculating presence on votes ...')
    save_sparse_people_presence_on_votes_between(playing_field, datetime_from, datetime_to)
    print('Calculating monthly presence on votes ...')
    save_people_monthly_presence_on_votes(playing_field, datetime_to)
    print('Done.')
