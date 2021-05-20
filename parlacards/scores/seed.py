from datetime import datetime, timedelta

from parladata.models.organization import Organization

from parlacards.scores.vocabulary_size import save_sparse_vocabulary_sizes_between

def calculate_sparse_scores(playing_field):
    datetime_to = datetime.now()
    datetime_from = datetime_to - timedelta(days=100)

    save_sparse_vocabulary_sizes_between(playing_field, datetime_from, datetime_to)
