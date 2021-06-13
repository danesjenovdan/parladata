from datetime import datetime

import pytest

from rest_framework.test import APIClient

from parlacards.views import *

client = APIClient()

@pytest.mark.django_db()
def test_misc_views():
    response = client.get('/v3/cards/misc/members/?id=1')
    assert response.status_code == 200

    response = client.get('/v3/cards/misc/members/?id=1')
    assert response.status_code == 200

    response = client.get('/v3/cards/misc/groups/?id=1')
    assert response.status_code == 200

    response = client.get('/v3/cards/misc/sessions/?id=1')
    assert response.status_code == 200

    response = client.get('/v3/cards/misc/legislation/?id=1')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_person_views():
    response = client.get('/v3/cards/person/basic-information/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/person/vocabulary-size/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/person/votes/?id=6')
    assert response.status_code == 200

    # TODO there are no questions in the test database
    response = client.get('/v3/cards/person/questions/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/person/memberships/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/person/most-votes-in-common/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/person/least-votes-in-common/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/person/deviation-from-group/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/person/average-number-of-speeches-per-session/?id=6')
    assert response.status_code == 200

    # TODO there are no questions in the test database
    response = client.get('/v3/cards/person/number-of-questions/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/person/vote-attendance/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/person/recent-activity/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/person/monthly-vote-attendance/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/person/style-scores/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/person/number-of-spoken-words/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/person/tfidf/?id=6')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_group_views():
    response = client.get('/v3/cards/group/basic-information/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/group/members/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/group/vocabulary-size/?id=6')
    assert response.status_code == 200

    # TODO there are no questions in the test database
    response = client.get('/v3/cards/group/number-of-questions/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/group/monthly-vote-attendance/?id=6')
    assert response.status_code == 200

    # TODO there are no questions in the test database
    response = client.get('/v3/cards/group/questions/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/group/vote-attendance/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/group/votes/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/group/most-votes-in-common/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/group/least-votes-in-common/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/group/deviation-from-group/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/group/tfidf/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/group/style-scores/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/group/discord/?id=6')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_session_views():
    response = client.get('/v3/cards/session/legislation/?id=1')
    assert response.status_code == 200

    response = client.get('/v3/cards/session/speeches/?id=1')
    assert response.status_code == 200

    response = client.get('/v3/cards/session/votes/?id=1')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_single_views():
    response = client.get('/v3/cards/speech/single/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/vote/single/?id=6')
    assert response.status_code == 200

    response = client.get('/v3/cards/session/single/?id=1')
    assert response.status_code == 200
