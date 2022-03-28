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
            use_idf=True,
            sublinear_tf=True
        )

        tfidf = tfidfVectorizer.fit_transform(speeches[language_code])
        feature_names = tfidfVectorizer.get_feature_names_out()

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

    # print statement for easier test updates
    # print(
    #     tfidfs[6]['tfidf'][0][0],
    #     tfidfs[6]['tfidf'][0][1],
    #     tfidfs[6]['tfidf'][1][0],
    #     tfidfs[6]['tfidf'][1][1],
    #     tfidfs[12]['tfidf'][0][0],
    #     tfidfs[12]['tfidf'][0][1],
    #     tfidfs[12]['tfidf'][-1][0],
    #     tfidfs[12]['tfidf'][-1][1],
    #     tfidfs[-1]['tfidf'][0][0],
    #     tfidfs[-1]['tfidf'][0][1]
    # )

    assert len(tfidfs) == 44
    assert len(tfidfs[0]['tfidf']) == 30

    assert tfidfs[6]['tfidf'][0][0] == ''
    assert tfidfs[6]['tfidf'][0][1] == 1.0

    assert tfidfs[6]['tfidf'][1][0] == '0'
    assert tfidfs[6]['tfidf'][1][1] == 0.0

    assert tfidfs[12]['tfidf'][0][0] == 'Toška'
    assert tfidfs[12]['tfidf'][0][1] == 0.19983805315026645

    assert tfidfs[12]['tfidf'][-1][0] == 'hitr'
    assert tfidfs[12]['tfidf'][-1][1] == 0.09290127788454586

    assert tfidfs[-1]['tfidf'][0][0] == 'navzočnost'
    assert tfidfs[-1]['tfidf'][0][1] == 0.05934929513712458

@pytest.mark.django_db()
def test_calculate_groups_tfidf(
    main_organization
):
    tfidfs = calculate_groups_tfidf(main_organization)

    # print statement for easier test updates
    # print(
    #     tfidfs[6]['tfidf'][0][0],
    #     tfidfs[6]['tfidf'][0][1],
    #     tfidfs[6]['tfidf'][1][0],
    #     tfidfs[6]['tfidf'][1][1],
    #     tfidfs[0]['tfidf'][0][0],
    #     tfidfs[0]['tfidf'][0][1],
    #     tfidfs[0]['tfidf'][-1][0],
    #     tfidfs[0]['tfidf'][-1][1],
    #     tfidfs[1]['tfidf'][0][0],
    #     tfidfs[1]['tfidf'][0][1]
    # )

    assert len(tfidfs) == 7
    assert len(tfidfs[0]['tfidf']) == 30

    assert tfidfs[6]['tfidf'][0][0] == 'komisija'
    assert tfidfs[6]['tfidf'][0][1] == 0.10010812317364043

    assert tfidfs[6]['tfidf'][1][0] == 'statutarno'
    assert tfidfs[6]['tfidf'][1][1] == 0.09649905369990573

    assert tfidfs[0]['tfidf'][0][0] == 'stanovanje'
    assert tfidfs[0]['tfidf'][0][1] == 0.13122290537166734

    assert tfidfs[0]['tfidf'][-1][0] == 'prostorski'
    assert tfidfs[0]['tfidf'][-1][1] == 0.07537407386637515

    assert tfidfs[1]['tfidf'][0][0] == 'prehod'
    assert tfidfs[1]['tfidf'][0][1] == 0.291176576653666

@pytest.mark.django_db()
def test_calculate_sessions_tfidf(
    main_organization
):
    tfidfs = calculate_sessions_tfidf(main_organization)

    # print statement for easier test updates
    # print(
    #     tfidfs[0]['tfidf'][0][0],
    #     tfidfs[0]['tfidf'][0][1],
    #     tfidfs[0]['tfidf'][1][0],
    #     tfidfs[0]['tfidf'][1][1],
    #     tfidfs[1]['tfidf'][0][0],
    #     tfidfs[1]['tfidf'][0][1],
    #     tfidfs[1]['tfidf'][1][0],
    #     tfidfs[1]['tfidf'][1][1],
    #     tfidfs[1]['tfidf'][-2][0],
    #     tfidfs[1]['tfidf'][-2][1]
    # )

    assert len(tfidfs) == 2
    assert len(tfidfs[0]['tfidf']) == 30

    assert tfidfs[0]['tfidf'][0][0] == 'nadzoren'
    assert tfidfs[0]['tfidf'][0][1] == 0.05251433636779131

    assert tfidfs[0]['tfidf'][1][0] == 'proračunski'
    assert tfidfs[0]['tfidf'][1][1] == 0.05086083980941219

    assert tfidfs[1]['tfidf'][0][0] == 'dom'
    assert tfidfs[1]['tfidf'][0][1] == 0.06647726021692574

    assert tfidfs[1]['tfidf'][1][0] == 'predlog'
    assert tfidfs[1]['tfidf'][1][1] == 0.06253020335090285

    assert tfidfs[1]['tfidf'][-2][0] == 'besedilo'
    assert tfidfs[1]['tfidf'][-2][1] == 0.04770457227442512
