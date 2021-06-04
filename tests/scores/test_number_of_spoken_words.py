from datetime import datetime

import pytest

from parladata.models.speech import Speech

from parlacards.scores.number_of_spoken_words import calculate_number_of_spoken_words

from tests.fixtures.common import *

@pytest.mark.django_db()
def test_calculate_number_of_spoken_words(
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

    number_of_spoken_words = calculate_number_of_spoken_words(first_person_speeches)
    assert number_of_spoken_words == 0

    number_of_spoken_words = calculate_number_of_spoken_words(second_person_speeches)
    assert number_of_spoken_words == 1543

    number_of_spoken_words = calculate_number_of_spoken_words(last_person_speeches)
    assert number_of_spoken_words == 157
