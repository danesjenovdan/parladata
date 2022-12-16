from datetime import datetime

import pytest

from rest_framework.test import APIClient

from parlacards.views import *

client = APIClient()

@pytest.mark.django_db()
def test_misc_members():
    response = client.get('/v3/cards/misc/members/?id=1&members:per_page=10&members:page=1&text=&order_by=name&preferred_pronoun=she')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_misc_groups():
    response = client.get('/v3/cards/misc/groups/?id=1')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_misc_sessions():
    response = client.get('/v3/cards/misc/sessions/?id=1')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_misc_legislation():
    response = client.get('/v3/cards/misc/legislation/?id=1')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_misc_last_session():
    response = client.get('/v3/cards/misc/last-session/?id=1')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_misc_search():
    response = client.get('/v3/cards/misc/search/?id=1')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_misc_menu_search():
    response = client.get('/v3/cards/misc/menu-search/?id=1')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_misc_basic_information():
    response = client.get('/v3/cards/misc/basic-information/?id=1')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_person_basic_information():
    response = client.get('/v3/cards/person/basic-information/?id=240')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_person_vocabulary_size():
    response = client.get('/v3/cards/person/vocabulary-size/?id=240')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_person_votes():
    response = client.get('/v3/cards/person/votes/?id=240')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_person_questions():
    # TODO we should also test the questions aren't all the same
    response = client.get('/v3/cards/person/questions/?id=240')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_person_memberships():
    response = client.get('/v3/cards/person/memberships/?id=240')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_person_most_votes_in_common():
    response = client.get('/v3/cards/person/most-votes-in-common/?id=240')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_person_least_votes_in_common():
    response = client.get('/v3/cards/person/least-votes-in-common/?id=240')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_person_deviation_from_group():
    response = client.get('/v3/cards/person/deviation-from-group/?id=240')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_person_average_number_of_speeches_per_session():
    response = client.get('/v3/cards/person/average-number-of-speeches-per-session/?id=240')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_person_questions():
    response = client.get('/v3/cards/person/number-of-questions/?id=240')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_person_vote_attendance():
    response = client.get('/v3/cards/person/vote-attendance/?id=240')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_person_recent_activity():
    response = client.get('/v3/cards/person/recent-activity/?id=240')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_person_monthly_vote_attendance():
    response = client.get('/v3/cards/person/monthly-vote-attendance/?id=240')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_person_style_scores():
    response = client.get('/v3/cards/person/style-scores/?id=240')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_person_number_of_spoken_words():
    response = client.get('/v3/cards/person/number-of-spoken-words/?id=240')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_person_tfidf():
    response = client.get('/v3/cards/person/tfidf/?id=240')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_person_media_reports():
    response = client.get('/v3/cards/person/media-reports/?id=240')
    assert response.status_code == 200

# TODO: needs settings.SOLR_URL
# @pytest.mark.django_db()
# def test_person_speeches():
#     response = client.get('/v3/cards/person/speeches/?id=19')
#     assert response.status_code == 200

@pytest.mark.django_db()
def test_group_basic_information():
    response = client.get('/v3/cards/group/basic-information/?id=19')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_group_members():
    response = client.get('/v3/cards/group/members/?id=19')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_group_vocabulary_size():
    response = client.get('/v3/cards/group/vocabulary-size/?id=19')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_group_number_of_questions():
    response = client.get('/v3/cards/group/number-of-questions/?id=19')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_group_monthly_vote_attendance():
    response = client.get('/v3/cards/group/monthly-vote-attendance/?id=19')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_group_questions():
    # TODO we should also test the questions aren't all the same
    response = client.get('/v3/cards/group/questions/?id=19')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_group_vote_attendance():
    response = client.get('/v3/cards/group/vote-attendance/?id=19')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_group_votes():
    response = client.get('/v3/cards/group/votes/?id=19')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_group_most_votes_in_common():
    response = client.get('/v3/cards/group/most-votes-in-common/?id=19')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_group_least_votes_in_common():
    response = client.get('/v3/cards/group/least-votes-in-common/?id=19')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_group_deviation_from_group():
    response = client.get('/v3/cards/group/deviation-from-group/?id=19')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_group_tfidf():
    response = client.get('/v3/cards/group/tfidf/?id=19')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_group_style_scores():
    response = client.get('/v3/cards/group/style-scores/?id=19')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_group_discord():
    response = client.get('/v3/cards/group/discord/?id=19')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_group_discord_with_nonexistent_id():
    response = client.get('/v3/cards/group/discord/?id=12000')
    assert response.status_code == 404

@pytest.mark.django_db()
def test_group_media_reports():
    response = client.get('/v3/cards/group/media-reports/?id=19')
    assert response.status_code == 200

# TODO: needs settings.SOLR_URL
# @pytest.mark.django_db()
# def test_group_speeches():
#     response = client.get('/v3/cards/group/speeches/?id=19')
#     assert response.status_code == 200

@pytest.mark.django_db()
def test_session_legislation():
    response = client.get('/v3/cards/session/legislation/?id=3782')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_session_speeches():
    response = client.get('/v3/cards/session/speeches/?id=3782')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_session_votes():
    response = client.get('/v3/cards/session/votes/?id=3782')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_session_votes():
    response = client.get('/v3/cards/session/tfidf/?id=3782')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_single_speech():
    response = client.get('/v3/cards/speech/single/?id=68974')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_single_vote():
    response = client.get('/v3/cards/vote/single/?id=10229')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_single_vote_with_only_anonymous_ballots():
    response = client.get('/v3/cards/vote/single/?id=10229')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_single_vote_with_some_anonymous_ballots():
    response = client.get('/v3/cards/vote/single/?id=10229')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_single_vote_without_ballots():
    response = client.get('/v3/cards/vote/single/?id=10229')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_single_session():
    response = client.get('/v3/cards/session/single/?id=3782')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_session_agenda_items():
    response = client.get('/v3/cards/session/agenda-items/?id=3782')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_session_minutes():
    response = client.get('/v3/cards/session/minutes/?id=3782')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_single_law():
    response = client.get('/v3/cards/legislation/single/?id=1403')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_single_minutes():
    response = client.get('/v3/cards/minutes/single/?id=28813')
    assert response.status_code == 200

# TODO: needs settings.SOLR_URL
# @pytest.mark.django_db()
# def test_search_speeches():
#     response = client.get('/v3/cards/search/speeches/?id=1')
#     assert response.status_code == 200

# TODO: needs settings.SOLR_URL
# @pytest.mark.django_db()
# def test_search_most_used_by_people():
#     response = client.get('/v3/cards/search/most-used-by-people/?id=1')
#     assert response.status_code == 200

# TODO: needs settings.SOLR_URL
# @pytest.mark.django_db()
# def test_search_usage_by_group():
#     response = client.get('/v3/cards/search/usage-by-group/?id=1')
#     assert response.status_code == 200

# TODO: needs settings.SOLR_URL
# @pytest.mark.django_db()
# def test_search_usage_through_time():
#     response = client.get('/v3/cards/search/usage-through-time/?id=1')
#     assert response.status_code == 200

@pytest.mark.django_db()
def test_search_votes():
    response = client.get('/v3/cards/search/votes/?id=1')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_search_legislation():
    response = client.get('/v3/cards/search/legislation/?id=1')
    assert response.status_code == 200

@pytest.mark.django_db()
def test_create_and_get_quote():
    response = client.post(
        '/v3/cards/speech/quote/',
        {
            'speech': 68974,
            'start_index': 6,
            'end_index': 9,
            'quote_content': 'dan'
        }
    )
    assert response.status_code == 201

    response = client.get('/v3/cards/speech/quote/?id=1')
    assert response.status_code == 200


@pytest.mark.django_db()
def test_public_person_question():
    response = client.post(
        '/v3/cards/person/public-questions/?id=1',
        {
            'recaptcha': 'token',
            'author_email': 'ivan@email.com',
            'text': 'what what what',
            'recipient_person': 240
        }
    )
    assert response.status_code == 201

    response = client.get('/v3/cards/person/public-questions/?id=1')
    assert response.status_code == 200
    assert len(response.json()['results']) == 1


@pytest.mark.django_db()
def test_validation_error_on_create_quote():
    response = client.post(
        '/v3/cards/speech/quote/',
        {
            'speech': 68974,
            'start_index': 6,
            'end_index': 10,
            'quote_content': 'ivan'
        }
    )
    assert response.status_code == 400
    assert 'quote_content' in response.json().keys()
