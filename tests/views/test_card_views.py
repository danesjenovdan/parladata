from datetime import datetime

import pytest

from rest_framework.test import APIRequestFactory

from parlacards.views import *

def get_card_response(url, card_id, card_date=datetime.now()):
    factory = APIRequestFactory()
    view = PersonInfo.as_view()
    request = factory.get(url)
    request.card_id = card_id
    request.card_date = card_date

    return view(request)

@pytest.mark.django_db()
def test_misc_views():
    response = get_card_response('/v3/cards/misc/members/', 1)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/misc/groups/', 1)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/misc/sessions/', 1)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/misc/legislation/', 1)
    assert response.status_code == 200

@pytest.mark.django_db()
def test_person_views():
    response = get_card_response('/v3/cards/person/basic-information/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/person/vocabulary-size/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/person/votes/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/person/questions/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/person/memberships/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/person/most-votes-in-common/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/person/least-votes-in-common/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/person/deviation-from-group/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/person/average-number-of-speeches-per-session/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/person/number-of-questions/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/person/vote-attendance/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/person/recent-activity/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/person/monthly-vote-attendance/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/person/style-scores/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/person/number-of-spoken-words/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/person/tfidf/', 6)
    assert response.status_code == 200

@pytest.mark.django_db()
def test_group_views():
    response = get_card_response('/v3/cards/group/basic-information/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/group/members/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/group/vocabulary-size/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/group/number-of-questions/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/group/monthly-vote-attendance/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/group/questions/', 6)
    assert response.status_code == 200

@pytest.mark.django_db()
def test_session_views():
    response = get_card_response('/v3/cards/session/legislation/', 1)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/session/speeches/', 1)
    assert response.status_code == 200

@pytest.mark.django_db()
def test_single_views():
    response = get_card_response('/v3/cards/speech/single/', 6)
    assert response.status_code == 200

    response = get_card_response('/v3/cards/vote/single/', 6)
    assert response.status_code == 200
