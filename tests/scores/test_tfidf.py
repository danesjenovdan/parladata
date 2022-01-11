import pytest

from sklearn.feature_extraction.text import TfidfVectorizer

from parlacards.scores.common import get_lemmatize_method
from parlacards.scores.tfidf import calculate_people_tfidf, calculate_groups_tfidf, calculate_sessions_tfidf

from tests.fixtures.common import *

def test_stopwords():
    # TODO these should probably be globals
    languages = ['sl', 'ua']
    speeches = {
        'sl': [
            'ena dva tri hvala',
            'pet sedem ne hvala prosim se vidimo'
        ],
        'ua': [
            'дяк шановн головуюч шановн колег я хоч сьогодн звернут до',
            'депутатів фракці слуг народ нагад вам що у назв ваш фракці є посиланн на народ'
        ]
    }

    for language_code in languages:
        get_stopwords = get_lemmatize_method('get_stopwords', language_code)
        tfidfVectorizer = TfidfVectorizer(
            lowercase=False, # do not transform to lowercase
            preprocessor=lambda x: x, # do not preprocess
            tokenizer=lambda x: x.split(' '), # tokenize by splitting at ' '
            stop_words=get_stopwords(),
            use_idf=True
        )

        tfidf = tfidfVectorizer.fit_transform(speeches[language_code])
        feature_names = tfidfVectorizer.get_feature_names()

        assert 'hvala' not in feature_names
        assert 'ena' not in feature_names
        assert 'se' not in feature_names
        assert 'я' not in feature_names
        assert 'є' not in feature_names


@pytest.mark.django_db()
def test_calculate_people_tfidf(
    main_organization
):
    tfidfs = calculate_people_tfidf(main_organization)

    assert len(tfidfs) == 44
    assert len(tfidfs[0]['tfidf']) == 30

    assert tfidfs[6]['tfidf'][0][0] == ''
    assert tfidfs[6]['tfidf'][0][1] == 1.0

    assert tfidfs[6]['tfidf'][1][0] == '0'
    assert tfidfs[6]['tfidf'][1][1] == 0.0

    assert tfidfs[12]['tfidf'][0][0] == 'Toška'
    assert tfidfs[12]['tfidf'][0][1] == 0.27739371672680996

    assert tfidfs[12]['tfidf'][-1][0] == 'noben'
    assert tfidfs[12]['tfidf'][-1][1] == 0.10700431242678085

    assert tfidfs[-1]['tfidf'][0][0] == 'prositi'
    assert tfidfs[-1]['tfidf'][0][1] == 0.24103916186682672

@pytest.mark.django_db()
def test_calculate_groups_tfidf(
    main_organization
):
    tfidfs = calculate_groups_tfidf(main_organization)

    assert len(tfidfs) == 7
    assert len(tfidfs[0]['tfidf']) == 30

    assert tfidfs[6]['tfidf'][0][0] == 'praven'
    assert tfidfs[6]['tfidf'][0][1] == 0.28916923723526916

    assert tfidfs[6]['tfidf'][1][0] == 'komisija'
    assert tfidfs[6]['tfidf'][1][1] == 0.2819182381993111

    assert tfidfs[0]['tfidf'][0][0] == 'stanovanje'
    assert tfidfs[0]['tfidf'][0][1] == 0.2551637453343532

    assert tfidfs[0]['tfidf'][-1][0] == 'bistvo'
    assert tfidfs[0]['tfidf'][-1][1] == 0.10590391095529379

    assert tfidfs[1]['tfidf'][0][0] == 'prehod'
    assert tfidfs[1]['tfidf'][0][1] == 0.5185699199364557

@pytest.mark.django_db()
def test_calculate_sessions_tfidf(
    main_organization
):
    tfidfs = calculate_sessions_tfidf(main_organization)

    assert len(tfidfs) == 2
    assert len(tfidfs[0]['tfidf']) == 30

    assert tfidfs[0]['tfidf'][0][0] == 'šport'
    assert tfidfs[0]['tfidf'][0][1] == 0.24828183478484658

    assert tfidfs[0]['tfidf'][1][0] == 'predlog'
    assert tfidfs[0]['tfidf'][1][1] == 0.20547462189090754

    assert tfidfs[1]['tfidf'][0][0] == 'predlog'
    assert tfidfs[1]['tfidf'][0][1] == 0.2724627492253146

    assert tfidfs[1]['tfidf'][1][0] == 'javen'
    assert tfidfs[1]['tfidf'][1][1] == 0.2681379436820556

    assert tfidfs[1]['tfidf'][-2][0] == 'prostorski'
    assert tfidfs[1]['tfidf'][-2][1] == 0.0908209164084382
