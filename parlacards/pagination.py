from django.core.paginator import Paginator
from django.utils.functional import cached_property

from parlacards.solr import get_speeches_from_solr


def valid_positive_int(number, default):
    try:
        if isinstance(number, float) and not number.is_integer():
            raise ValueError
        number = int(number)
    except (TypeError, ValueError):
        number = default
    if number < 1:
        number = default
    return number


def parse_pagination_query_params(params, prefix=''):
    requested_page = valid_positive_int(params.get(f'{prefix}page', None), 1)
    requested_per_page = valid_positive_int(params.get(f'{prefix}per_page', None), 10)

    return (requested_page, requested_per_page)


def pagination_response_data(paginator, page, prefix=''):
    return {
        f'{prefix}count': paginator.count,
        f'{prefix}pages': paginator.num_pages,
        f'{prefix}page': page.number,
        f'{prefix}per_page': paginator.per_page
    }


class SolrPaginator(Paginator):
    def __init__(self, solr_params, per_page, orphans=0,
                 allow_empty_first_page=True):
        self.solr_params = solr_params
        self.object_list = None
        self.per_page = int(per_page)
        self.orphans = int(orphans)
        self.allow_empty_first_page = allow_empty_first_page

    @cached_property
    def count(self):
        """Return the total number of objects, across all pages."""
        _, count = get_speeches_from_solr(**self.solr_params, page=1, per_page=0)
        return count

    def page(self, number):
        """Return a Page object for the given 1-based page number."""
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        # I'm not sure why this is called bottom and top, but Paginator slices
        # object_list like this `object_list[bottom:top]`
        objects, _ = get_speeches_from_solr(**self.solr_params, page=number, per_page=top-bottom)
        return self._get_page(objects, number, self)
