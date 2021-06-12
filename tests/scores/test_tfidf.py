import pytest

from parlacards.scores.tfidf import calculate_people_tfidf, calculate_groups_tfidf

from tests.fixtures.common import *

@pytest.mark.django_db()
def test_calculate_people_tfidf(
    main_organization
):
    tfidfs = calculate_people_tfidf(main_organization)
    
    assert len(tfidfs) == 43
    assert len(tfidfs[0]['tfidf']) == 20

    assert tfidfs[6]['tfidf'][0][0] == 'študija'
    assert tfidfs[6]['tfidf'][0][1] == 0.2744569242313267

    assert tfidfs[6]['tfidf'][1][0] == 'realizacija'
    assert tfidfs[6]['tfidf'][1][1] == 0.25645000829806014

    assert tfidfs[12]['tfidf'][0][0] == 'zdravstven'
    assert tfidfs[12]['tfidf'][0][1] == 0.32444499263889226

    assert tfidfs[12]['tfidf'][-1][0] == 'vsebovati'
    assert tfidfs[12]['tfidf'][-1][1] == 0.11160843758538196

    assert tfidfs[-1]['tfidf'][0][0] == 'kolegica'
    assert tfidfs[-1]['tfidf'][0][1] == 0.3453825908498845

@pytest.mark.django_db()
def test_calculate_groups_tfidf(
    main_organization
):
    tfidfs = calculate_groups_tfidf(main_organization)
    
    assert len(tfidfs) == 7
    assert len(tfidfs[0]['tfidf']) == 20

    assert tfidfs[6]['tfidf'][0][0] == 'hvala'
    assert tfidfs[6]['tfidf'][0][1] == 0.3400814800464829

    assert tfidfs[6]['tfidf'][1][0] == 'praven'
    assert tfidfs[6]['tfidf'][1][1] == 0.30563348367768445

    assert tfidfs[0]['tfidf'][0][0] == ''
    assert tfidfs[0]['tfidf'][0][1] == 1.0

    assert tfidfs[0]['tfidf'][-1][0] == '1661'
    assert tfidfs[0]['tfidf'][-1][1] == 0.0

    assert tfidfs[1]['tfidf'][0][0] == 'vrtec'
    assert tfidfs[1]['tfidf'][0][1] == 0.2978023199873716
