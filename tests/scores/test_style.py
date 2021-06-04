from datetime import datetime

import pytest

from parladata.models.speech import Speech

from parlacards.scores.style import calculate_style_score, get_styled_lemmas

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

    problematic_style = calculate_style_score(first_person_speeches, get_styled_lemmas('problematic'))
    simple_style = calculate_style_score(first_person_speeches, get_styled_lemmas('simple'))
    sophisticated_style = calculate_style_score(first_person_speeches, get_styled_lemmas('sophisticated'))

    assert problematic_style == 0
    assert simple_style == 0
    assert sophisticated_style == 0

    problematic_style = calculate_style_score(second_person_speeches, get_styled_lemmas('problematic'))
    simple_style = calculate_style_score(second_person_speeches, get_styled_lemmas('simple'))
    sophisticated_style = calculate_style_score(second_person_speeches, get_styled_lemmas('sophisticated'))

    assert problematic_style == 0.8421052631578947
    assert simple_style == 1.8947368421052633
    assert sophisticated_style == 4.421052631578947

    problematic_style = calculate_style_score(last_person_speeches, get_styled_lemmas('problematic'))
    simple_style = calculate_style_score(last_person_speeches, get_styled_lemmas('simple'))
    sophisticated_style = calculate_style_score(last_person_speeches, get_styled_lemmas('sophisticated'))

    assert problematic_style == 2.2222222222222223
    assert simple_style == 3.3333333333333335
    assert sophisticated_style == 7.777777777777778
