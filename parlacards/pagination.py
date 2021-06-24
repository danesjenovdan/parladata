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


def parse_pagination_query_params(params):
    requested_page = valid_positive_int(params.get('page', None), 1)
    requested_per_page = valid_positive_int(params.get('per_page', None), 10)

    return (requested_page, requested_per_page)
