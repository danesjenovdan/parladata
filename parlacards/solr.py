import re

import requests

from django.conf import settings

from parladata.models.speech import Speech

def solr_select(
    text_query='*',
    person_id=None,
    group_id=None,
    highlight=False,
    facet=False,
    rows_per_page=20,
    document_type='speech'
):
    # TODO solr timeout
    # TODO solr offline
    q_params = f'{text_query} AND type:{document_type}'
    if person_id:
        q_params += f' AND person_id:{person_id}'
    if group_id:
        q_params += f' AND party_id:{group_id}' # TODO rename to group_id

    params = {
        'wt': 'json',
        'sort': 'start_time desc',
        'rows': rows_per_page,
        'start': 0, # TODO implement paging like django native
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
    person_id=None,
    group_id=None,
    highlight=False,
    facet=False,
    rows_per_page=20,
    document_type='speech'
):
    solr_response = solr_select(
        text_query=text_query,
        person_id=person_id,
        group_id=group_id,
        highlight=highlight,
        facet=facet,
        rows_per_page=rows_per_page,
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

    return speeches