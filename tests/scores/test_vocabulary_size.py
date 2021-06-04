from datetime import datetime

import pytest

from parladata.models.speech import Speech

from parlacards.scores.vocabulary_size import calculate_vocabulary_size

from tests.fixtures.common import *

@pytest.mark.django_db()
def test_calculate_vocabulary_size(
    first_person,
    second_person,
    last_person
):
    timestamp = datetime.now()

    first_person_speeches = Speech.objects.filter_valid_speeches(timestamp).filter(
        speaker=first_person,
        start_time__lte=timestamp
    ).values_list('lemmatized_content', flat=True)

    second_person_speeches = Speech.objects.filter_valid_speeches(timestamp).filter(
        speaker=second_person,
        start_time__lte=timestamp
    ).values_list('lemmatized_content', flat=True)

    last_person_speeches = Speech.objects.filter_valid_speeches(timestamp).filter(
        speaker=last_person,
        start_time__lte=timestamp
    ).values_list('lemmatized_content', flat=True)

    vocabulary_size = calculate_vocabulary_size(first_person_speeches)
    assert vocabulary_size == 0

    vocabulary_size = calculate_vocabulary_size(second_person_speeches)
    assert vocabulary_size == 0.01550261096605744

    vocabulary_size = calculate_vocabulary_size(last_person_speeches)
    assert vocabulary_size == 0.2112676056338028
