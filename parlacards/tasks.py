

from parlacards.scores.tfidf import save_groups_tfidf, save_people_tfidf, save_sessions_tfidf
from parlacards.utils import get_playing_fields

from parladata.models import Session

from datetime import datetime


def delay_method_on_playing_field(method):
    playing_fields = get_playing_fields(datetime.now())
    for playing_field in playing_fields:
        method(playing_field, timestamp=datetime.now())

def delay_members_tfidf_task():
    delay_method_on_playing_field(save_people_tfidf)


def delay_organization_tfidf_task():
    delay_method_on_playing_field(save_groups_tfidf)


def delay_sessions_tfidf_task(**kwargs):
    session = Session.objects.filter(id=kwargs['id']).first()
    if session:
        save_sessions_tfidf(session)


