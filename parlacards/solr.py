import re
from datetime import datetime, timedelta

import requests

from django.conf import settings

from parladata.models.speech import Speech

def one_month_later(date, shorten_for=0):
    # damn date math
    try:
        end_date = date.replace(month=date.month+1) - timedelta(days=shorten_for)
    except ValueError:
        if date.month == 12:
            end_date = date.replace(year=date.year+1, month=1) - timedelta(days=shorten_for)
        else:
            # next month is too short to have "same date"
            # pick your own heuristic, or re-raise the exception:
            one_month_later(date, shorten_for=(shorten_for + 1))

    return end_date

def process_month_string(month_string):
    year, month = map(
        lambda x: int(x),
        month_string.split('-')
    )

    start_date = datetime(
        year=year,
        month=month,
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    end_date = one_month_later(start_date) - timedelta(microseconds=1)

    return f'[{start_date.isoformat()}Z TO {end_date.isoformat()}Z]'

def solr_select(
    text_query='*',
    people_ids=[],
    group_ids=[],
    months=[],
    highlight=False,
    facet=False,
    page=1,
    per_page=20,
    document_type='speech'
):
    # TODO solr timeout
    # TODO solr offline
    q_params = f'{text_query} AND type:{document_type}'
    if people_ids:
        q_params += f' AND person_id:({" OR ".join(map(lambda x: str(x), people_ids))})'
    if group_ids:
        q_params += f' AND party_id:({" OR ".join(map(lambda x: str(x), group_ids))})' # TODO rename to group_id
    if months:
        q_params += f' AND start_time:({" OR ".join(map(lambda x: process_month_string(x), months))})'

    params = {
        'wt': 'json',
        'sort': 'start_time desc',
        'rows': per_page,
        'start': (page - 1) * per_page,
        'q': q_params,
        'fl': 'speech_id'
    }

    if highlight:
        params['hl'] = 'true'
        params['hl.fl'] = 'content'

    if facet:
        params['facet'] = 'true'
        params['facet.field'] = ['person_id', 'party_id']
        params['facet.range'] = 'start_time'
        params['facet.range.gap'] = '+1MONTHS'
        # TODO
        # params['facet.range.start'] = f'{config.facetRangeStart}T00:00:00.000Z',
        # params['facet.range.end'] = config.facetRangeEnd ? `${config.facetRangeEnd}T00:00:00.000Z` : 'NOW',

    url = f'{settings.SOLR_URL}/select'
    response = requests.get(url, params=params)

    return response.json()

def shorten_highlighted_content(highlight, max_length=250):
    if len(highlight) <= max_length:
        return highlight

    try:
        first_opening_em_start_index = highlight.index('<em>')
        last_closing_em_end_index = highlight.rfind('</em>') + len('</em>')
    except ValueError:
        return highlight[:max_length] + '[...]'

    if last_closing_em_end_index <= max_length:
        # all highlights are within limits
        return f'{highlight[:max_length]}[...]'

    # not all highlights are withing limits
    # check if first highlight is visible
    # and trim the left side of the highlight
    if first_opening_em_start_index > (max_length / 2):
        left_trimmed_highlight = f'{highlight[first_opening_em_start_index:]}'
    else:
        left_trimmed_highlight = highlight

    # find closing tags that fit the limit
    closing_start_indexes = [
        m.start() for
        m in
        re.finditer('</em>', left_trimmed_highlight)
    ]
    legit_closing_start_indexes = [i for i in closing_start_indexes if i < max_length]

    trimmed_highlight = left_trimmed_highlight[:legit_closing_start_indexes[-1]] + '</em>'

    # check if trimmed_highlight is too short
    if len(trimmed_highlight) < (max_length / 2):
        trimmed_highlight_index = highlight.lower().index(trimmed_highlight.lower())

        # pad on left
        trimmed_highlight = '[...]' + highlight[
            (trimmed_highlight_index - int(max_length / 3)):trimmed_highlight_index
        ] + trimmed_highlight

        # pad on right
        after_trimmed_highlight_start_index = trimmed_highlight_index + len(trimmed_highlight)
        trimmed_highlight = trimmed_highlight + highlight[
            after_trimmed_highlight_start_index:(after_trimmed_highlight_start_index + int(max_length/3))
        ]

    return trimmed_highlight + '[...]'

def get_speeches_from_solr(
    text_query='*',
    people_ids=None,
    group_ids=None,
    months=[],
    highlight=False,
    facet=False,
    page=1,
    per_page=20,
    document_type='speech'
):
    solr_response = solr_select(
        text_query=text_query,
        people_ids=people_ids,
        group_ids=group_ids,
        months=months,
        highlight=highlight,
        facet=facet,
        page=page,
        per_page=per_page,
        document_type=document_type
    )

    speech_ids = [
        solr_doc['speech_id'] for
        solr_doc in solr_response['response']['docs']
    ]

    # get speeches into memory from the db
    speeches = list(Speech.objects.filter(
        id__in=speech_ids
    ))

    for speech in speeches:
        if solr_response['highlighting'].get(
            f'speech_{speech.id}',
            {}
        ).get(
            'content',
            False
        ):
            speech.content = '[...]'.join(
                solr_response['highlighting'][f'speech_{speech.id}']['content']
            )

        speech.content = shorten_highlighted_content(speech.content)

    return (speeches, solr_response['response']['numFound'])
