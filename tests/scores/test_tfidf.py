import pytest

from parlacards.scores.tfidf import calculate_people_tfidf

@pytest.mark.django_db
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
