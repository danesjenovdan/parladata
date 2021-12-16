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
    assert len(tfidfs[0]['tfidf']) == 20

    assert tfidfs[6]['tfidf'][0][0] == ''
    assert tfidfs[6]['tfidf'][0][1] == 1.0

    assert tfidfs[6]['tfidf'][1][0] == '0'
    assert tfidfs[6]['tfidf'][1][1] == 0.0

    assert tfidfs[12]['tfidf'][0][0] == 'Toška'
    assert tfidfs[12]['tfidf'][0][1] == 0.27097451584792537

    assert tfidfs[12]['tfidf'][-1][0] == 'zanimati'
    assert tfidfs[12]['tfidf'][-1][1] == 0.11016057523669014

    assert tfidfs[-1]['tfidf'][0][0] == 'prositi'
    assert tfidfs[-1]['tfidf'][0][1] == 0.2434688040513122

@pytest.mark.django_db()
def test_calculate_groups_tfidf(
    main_organization
):
    tfidfs = calculate_groups_tfidf(main_organization)

    assert len(tfidfs) == 7
    assert len(tfidfs[0]['tfidf']) == 20

    assert tfidfs[6]['tfidf'][0][0] == 'praven'
    assert tfidfs[6]['tfidf'][0][1] == 0.28127968808598186

    assert tfidfs[6]['tfidf'][1][0] == 'komisija'
    assert tfidfs[6]['tfidf'][1][1] == 0.2742265216888708

    assert tfidfs[0]['tfidf'][0][0] == 'stanovanje'
    assert tfidfs[0]['tfidf'][0][1] == 0.2503027804387077

    assert tfidfs[0]['tfidf'][-1][0] == 'glede'
    assert tfidfs[0]['tfidf'][-1][1] == 0.1065583828779338

    assert tfidfs[1]['tfidf'][0][0] == 'prehod'
    assert tfidfs[1]['tfidf'][0][1] == 0.5164697268796293

@pytest.mark.django_db()
def test_calculate_sessions_tfidf(
    main_organization
):
    tfidfs = calculate_sessions_tfidf(main_organization)

    assert len(tfidfs) == 2
    assert len(tfidfs[0]['tfidf']) == 20

    assert tfidfs[0]['tfidf'][0][0] == 'šport'
    assert tfidfs[0]['tfidf'][0][1] == 0.2404590143991407

    assert tfidfs[0]['tfidf'][1][0] == 'občina'
    assert tfidfs[0]['tfidf'][1][1] == 0.19692764110274455

    assert tfidfs[1]['tfidf'][0][0] == 'javen'
    assert tfidfs[1]['tfidf'][0][1] == 0.26546033377935546

    assert tfidfs[1]['tfidf'][1][0] == 'občina'
    assert tfidfs[1]['tfidf'][1][1] == 0.2440522423455365

    assert tfidfs[1]['tfidf'][-2][0] == 'ampak'
    assert tfidfs[1]['tfidf'][-2][1] == 0.09419560230880356
