from datetime import datetime, timedelta
from math import ceil, floor

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


def expand_highlighted_part(highlight, max_length, start_index, end_index):
    full_highlight_length = len(highlight)
    highlight_length = end_index - start_index
    remaining_length = max_length - highlight_length

    # add half of remaining length to the end of highlight slice and stop at end
    slice_end = min(floor(end_index + (remaining_length / 2)), full_highlight_length)
    # move slice end to the next space if it exists
    if slice_end < full_highlight_length and slice_end > end_index:
        last_space_index = highlight.rfind(' ', end_index, slice_end)
        slice_end = last_space_index - 1 if last_space_index != -1 else slice_end

    # recalculate remaining length
    highlight_length = slice_end - start_index
    remaining_length = max_length - highlight_length

    # add half of remaining length to the start of highlight slice and stop at beginning
    slice_start = max(ceil(start_index - (remaining_length / 2)), 0)
    # move slice start to the next space if it exists
    if slice_start > 0 and slice_start < start_index:
        first_space_index = highlight.find(' ', slice_start, start_index)
        slice_start = first_space_index + 1 if first_space_index != -1 else slice_start

    # recalculate remaining length
    highlight_length = slice_end - slice_start
    remaining_length = max_length - highlight_length

    # try adding all of the remaining length to the end of highlight slice and stop at end
    slice_end = min(slice_end + remaining_length, full_highlight_length)
    # move slice end to the next space if it exists
    if slice_end < full_highlight_length and slice_end > end_index:
        last_space_index = highlight.rfind(' ', end_index, slice_end)
        slice_end = last_space_index if last_space_index != -1 else slice_end

    highlight_slice = highlight[slice_start:slice_end]
    # if we have more opening tags than closing ones, close the last one
    if highlight_slice.count('<em>') > highlight_slice.count('</em>'):
        highlight_slice + '</em>'

    return f'{"[...] " if slice_start > 0 else ""}{highlight_slice}{" [...]" if slice_end < full_highlight_length else ""}'


def shorten_highlighted_content(highlight, max_length=250):
    full_highlight_length = len(highlight)

    if full_highlight_length <= max_length:
        return highlight

    try:
        first_opening_em_start_index = highlight.index('<em>')
        last_closing_em_end_index = highlight.rindex('</em>') + len('</em>')
        highlight_length = last_closing_em_end_index - first_opening_em_start_index
    except ValueError:
        return f'{highlight[:max_length]} [...]'

    if last_closing_em_end_index <= max_length:
        # all highlights are within limits
        last_space_index = highlight.rfind(' ', 0, max_length)
        if last_space_index != -1 and last_space_index > last_closing_em_end_index:
            return f'{highlight[:last_space_index]} [...]'
        return f'{highlight[:max_length]} [...]'

    if highlight_length == max_length:
        # all highlights fit exactly within limits
        return highlight[first_opening_em_start_index:last_closing_em_end_index]

    if highlight_length < max_length:
        # highlight is too short, add more text on both ends
        return expand_highlighted_part(highlight, max_length, first_opening_em_start_index, last_closing_em_end_index)

    # not all highlights are within limits
    # try including only first highlight
    try:
        first_closing_em_end_index = highlight.index('</em>') + len('</em>')
        highlight_length = first_closing_em_end_index - first_opening_em_start_index
    except ValueError:
        return f'{highlight[:max_length]} [...]'

    if highlight_length == max_length:
        # the single highlight fits exactly within limits
        slice_start = first_opening_em_start_index
        slice_end = first_closing_em_end_index
        return f'{"[...] " if slice_start > 0 else ""}{highlight[slice_start:slice_end]}{" [...]" if slice_end < full_highlight_length else ""}'

    if highlight_length > max_length:
        # the single highlight is too long, just trim it to max length and close the tag
        slice_start = first_opening_em_start_index
        slice_end = first_opening_em_start_index + max_length - len('</em>')
        last_space_index = highlight.rfind(' ', slice_start, slice_end)
        if last_space_index != -1:
            slice_end = last_space_index
        highlight_slice = highlight[slice_start:slice_end] + '</em>'
        return f'{"[...] " if slice_start > 0 else ""}{highlight_slice}{" [...]" if slice_end < full_highlight_length else ""}'

    # highlight is too short, add more text on both ends
    return expand_highlighted_part(highlight, max_length, first_opening_em_start_index, first_closing_em_end_index)


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
        if solr_response['highlighting'].get(f'speech_{speech.id}', {}).get('content', False):
            speech.content = '[...]'.join(
                solr_response['highlighting'][f'speech_{speech.id}']['content']
            )

        speech.content = shorten_highlighted_content(speech.content)

    return (speeches, solr_response['response']['numFound'])
