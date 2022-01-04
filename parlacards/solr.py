from datetime import datetime, timedelta
from math import ceil, floor

import requests

from django.conf import settings

from sentry_sdk import capture_message

from parladata.models.speech import Speech
from parladata.models.vote import Vote
from parladata.models.legislation import Law


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
    document_type='speech',
    fl='speech_id',
    mandate=None
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
    if mandate:
        q_params += f' AND term:{mandate}'

    params = {
        'wt': 'json',
        'sort': 'start_time desc',
        'rows': per_page,
        'start': (page - 1) * per_page,
        'q': q_params,
        'fl': fl
    }

    if highlight:
        params['hl'] = 'true'
        params['hl.fl'] = 'content'

    if facet:
        params['facet'] = 'true'
        params['facet.field'] = ['person_id', 'party_id']
        params['facet.range'] = 'start_time'
        params['facet.range.gap'] = '+1MONTHS'
        # TODO proper facet start
        # params['facet.range.start'] = f'{config.facetRangeStart}T00:00:00.000Z',
        # params['facet.range.end'] = config.facetRangeEnd ? `${config.facetRangeEnd}T00:00:00.000Z` : 'NOW',
        params['facet.range.start'] = f'2018-12-15T00:00:00.000Z'
        params['facet.range.end'] = 'NOW'

    url = f'{settings.SOLR_URL}/select'
    response = requests.get(url, params=params, timeout=30)

    # die informatively when Solr is unreachable
    if response.status_code >= 400:
        capture_message(
            f'Solr unreachable at {settings.SOLR_URL}. Error {response.status_code}.',
            level="warning"
        )
        if response.status_code > 500:
            raise Exception(f'Solr unreachable at {settings.SOLR_URL}. Error {response.status_code}.')

        return {
            'response': {
                'docs': [],
                'numFound': 0,
            }
        }

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
        highlight_slice = highlight_slice + '</em>'

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
    document_type='speech',
    mandate=None
):
    #TODO make search by mandate
    solr_response = solr_select(
        text_query=text_query,
        people_ids=people_ids,
        group_ids=group_ids,
        months=months,
        highlight=highlight,
        facet=facet,
        page=page,
        per_page=per_page,
        document_type=document_type,
        mandate=mandate
    )

    speech_ids = [solr_doc['speech_id'] for solr_doc in solr_response['response']['docs']]

    # get speeches into memory from the db
    speeches = list(Speech.objects.filter(id__in=speech_ids))

    # if len(speech_ids) != len(speeches):
        # this means that solr still has old speech ids
        # most likely upload_speeches_to_solr was not run
        # TODO: report this error somehow

    for speech in speeches:
        if solr_response['highlighting'].get(f'speech_{speech.id}', {}).get('content', False):
            speech.content = '[...]'.join(
                solr_response['highlighting'][f'speech_{speech.id}']['content']
            )

        speech.content = shorten_highlighted_content(speech.content)

    return (speeches, solr_response['response']['numFound'])


def parse_search_query_params(params, **overrides):
    parsed_params = {}
    if params.get('text', False):
        parsed_params['text_query'] = params['text']
    if params.get('months', False):
        parsed_params['months'] = params['months'].split(',')
    if params.get('people', False):
        parsed_params['people_ids'] = params['people'].split(',')
    if params.get('groups', False):
        parsed_params['group_ids'] = params['groups'].split(',')
    if params.get('mandate', False):
        parsed_params['mandate'] = params['mandate']

    return {
        **parsed_params,
        **overrides,
    }


def get_votes_from_solr(text_query='*', mandate=None, page=1, per_page=20):
    solr_response = solr_select(
        text_query=text_query,
        page=page,
        per_page=per_page,
        document_type='vote',
        fl="vote_id",
        mandate=mandate
    )
    vote_ids = [solr_doc['vote_id'] for solr_doc in solr_response['response']['docs']]
    votes = list(Vote.objects.filter(id__in=vote_ids))
    return (votes, solr_response['response']['numFound'])


def get_legislation_from_solr(text_query='*', mandate=None, page=1, per_page=20):
    solr_response = solr_select(
        text_query=text_query,
        page=page,
        per_page=per_page,
        document_type='law',
        fl="law_id",
        mandate=mandate
    )
    law_ids = [solr_doc['law_id'] for solr_doc in solr_response['response']['docs']]
    legislation = list(Law.objects.filter(id__in=law_ids))
    return (legislation, solr_response['response']['numFound'])


def delete_solr_documents():
    headers = {
        'Content-Type': 'text/xml',
    }
    data = '<delete><query>*:*</query></delete>'

    response = requests.post(
        f'{settings.SOLR_URL}/update',
        headers=headers,
        data='<delete><query>*:*</query></delete>'
    )
    if response.status_code == 200:
        requests.post(
            f'{settings.SOLR_URL}/update',
            headers=headers,
            data='<commit />'
        )
