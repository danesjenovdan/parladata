from datetime import datetime, timedelta

def get_dates_between(datetime_from=datetime.now(), datetime_to=datetime.now()):
    number_of_days = (datetime_to - datetime_from).days

    return [(datetime_from + timedelta(days=i)) for i in range(number_of_days)]

def get_fortnights_between(datetime_from=datetime.now(), datetime_to=datetime.now()):
    number_of_fortnights = (datetime_to - datetime_from).days % 14

    return [(datetime_from + timedelta(days=(i * 14))) for i in range(number_of_fortnights)]
