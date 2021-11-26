import pytest

from parlacards.scores.tfidf import calculate_people_tfidf, calculate_groups_tfidf, calculate_sessions_tfidf

from tests.fixtures.common import *

@pytest.mark.django_db()
def test_calculate_people_tfidf(
    main_organization
):
    tfidfs = calculate_people_tfidf(main_organization)

    assert len(tfidfs) == 44
    assert len(tfidfs[0]['tfidf']) == 20

    assert tfidfs[6]['tfidf'][0][0] == ''
    assert tfidfs[6]['tfidf'][0][1] == 1.0

    assert tfidfs[6]['tfidf'][1][0] == '0'
    assert tfidfs[6]['tfidf'][1][1] == 0.0

    assert tfidfs[12]['tfidf'][0][0] == 'Toška'
    assert tfidfs[12]['tfidf'][0][1] == 0.2686323998804416

    assert tfidfs[12]['tfidf'][-1][0] == 'iti'
    assert tfidfs[12]['tfidf'][-1][1] == 0.11051996765237126

    assert tfidfs[-1]['tfidf'][0][0] == 'mesten'
    assert tfidfs[-1]['tfidf'][0][1] == 0.28052894450457266

@pytest.mark.django_db()
def test_calculate_groups_tfidf(
    main_organization
):
    tfidfs = calculate_groups_tfidf(main_organization)

    assert len(tfidfs) == 7
    assert len(tfidfs[0]['tfidf']) == 20

    assert tfidfs[6]['tfidf'][0][0] == 'hvala'
    assert tfidfs[6]['tfidf'][0][1] == 0.47177337609897546

    assert tfidfs[6]['tfidf'][1][0] == 'praven'
    assert tfidfs[6]['tfidf'][1][1] == 0.24012592068886013

    assert tfidfs[0]['tfidf'][0][0] == 'stanovanje'
    assert tfidfs[0]['tfidf'][0][1] == 0.24390870799836997

    assert tfidfs[0]['tfidf'][-1][0] == 'gradivo'
    assert tfidfs[0]['tfidf'][-1][1] == 0.10517674779057146

    assert tfidfs[1]['tfidf'][0][0] == 'prehod'
    assert tfidfs[1]['tfidf'][0][1] == 0.5071603819535089

@pytest.mark.django_db()
def test_calculate_sessions_tfidf(
    main_organization
):
    tfidfs = calculate_sessions_tfidf(main_organization)

    assert len(tfidfs) == 2
    assert len(tfidfs[0]['tfidf']) == 20

    assert tfidfs[0]['tfidf'][0][0] == 'mesten'
    assert tfidfs[0]['tfidf'][0][1] == 0.2966073474885689

    assert tfidfs[0]['tfidf'][1][0] == 'hvala'
    assert tfidfs[0]['tfidf'][1][1] == 0.29124697373877545

    assert tfidfs[1]['tfidf'][0][0] == 'Ljubljana'
    assert tfidfs[1]['tfidf'][0][1] == 0.29682546570565693

    assert tfidfs[1]['tfidf'][1][0] == 'mesten'
    assert tfidfs[1]['tfidf'][1][1] == 0.25651583456044424

    assert tfidfs[1]['tfidf'][-2][0] == 'akt'
    assert tfidfs[1]['tfidf'][-2][1] == 0.08794828613500946
