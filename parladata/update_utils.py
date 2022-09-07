from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils.translation import gettext as _
from django.contrib.auth.models import Group

from parladata.models.vote import Vote
from parladata.models.session import Session
from parladata.models.motion import Motion
from parladata.models.speech import Speech
from parladata.models.person import Person

from datetime import datetime, timedelta

import operator


"""
relativno navadno večino: (večina prisotnih poslancev; najpogostejši način odločanja),
absolutno navadno večino: (vsaj 46 glasov poslancev),
relativno kvalificirano večino: (2/3 prisotnih poslancev) ali
absolutno kvalificirano večino: (vsaj 60 glasov poslancev).
"""

def get_result_for_relative_normal_majority(vote):
    options = vote.get_option_counts()
    return options['for'] > options['against']

def get_result_for_absolute_normal_majority(vote):
    options = vote.get_option_counts()
    return options['for'] > (sum(options.values())/2 + 1)

def set_results_to_votes(majority='relative_normal'):
    for vote in Vote.objects.filter(result=None):
        if majority == 'absolute_normal':
            final_result = get_result_for_absolute_normal_majority(vote)
        else:
            final_result = get_result_for_relative_normal_majority(vote)

        motion = vote.motion
        motion.result = final_result
        motion.save()
        vote.result = final_result
        vote.save()

def pair_motions_with_speeches():
    for session in Session.objects.all():
        motions = session.motions.filter(speech=None)
        speeches_with_motion = session.speeches.filter(Q(content__contains='PROTI'), Q(content__contains='ZA'))
        contents = {speech.id: speech.content for speech in speeches_with_motion}
        for motion in motions:
            title = motion.title
            splitted_title = title.split(" ")
            scores = {}
            for speech_id, content in contents.items():
                score = 0.0
                for word in splitted_title:
                    if word in content:
                        score +=1
                scores[speech_id] = score/len(splitted_title)

            if scores:
                the_speech = max(scores.items(), key=operator.itemgetter(1))[0]
                speech = speeches_with_motion.get(id=the_speech)
                speech.motions.add(motion)
                score = scores[the_speech]
                speech.tags.add(str(int(score*10)*10))

def notify_editors_for_new_data():
    now = datetime.now()
    yeterday = now - timedelta(days=1)

    new_motions = Motion.objects.filter(created_at__gte=yeterday)
    new_speeches = Speech.objects.filter(created_at__gte=yeterday)
    editor_permission_group = Group.objects.filter(name__icontains="editor").first()
    sessions = [speech.session for  speech in new_speeches.distinct('session')]
    new_people = Person.objects.filter(created_at__gte=yeterday)
    new_voters = Person.objects.filter(ballots__isnull=False, person_memberships__isnull=True).distinct('id')

    new_votes_need_editing = Vote.objects.filter(created_at__gte=yeterday, needs_editing=True)

    assert bool(editor_permission_group), 'There\'s no editor permission group'

    if new_motions or new_speeches or new_people:
        for editor in editor_permission_group.user_set.all():
            send_email(
                _('New data for edit in parlameter ') + settings.INSTALATION_NAME,
                editor.email,
                'daily_notification.html',
                {
                    'base_url': settings.BASE_URL,
                    'new_motions': new_motions,
                    'new_speeches': new_speeches,
                    'sessions': sessions,
                    'new_voters': new_voters,
                    'new_people': new_people,
                    'new_votes_need_editing': new_votes_need_editing,
                    'instalation_name': settings.INSTALATION_NAME
                }
            )

def send_email(subject, to_email, template, data, from_email=settings.FROM_EMAIL):
    html_body = render_to_string(template, data)
    text_body = strip_tags(html_body)

    msg = EmailMultiAlternatives(
        subject=subject,
        from_email=from_email,
        to=[to_email],
        body=text_body)
    msg.attach_alternative(html_body, "text/html")
    msg.send()

def set_vote_session(print_method=print):
    sessions = Session.objects.all().order_by('start_time')
    session_count = sessions.count()
    for idx, session in enumerate(sessions):
        start_time = session.start_time
        if idx + 1 < session_count:
            end_time = sessions[idx + 1].start_time
        else:
            end_time = datetime.max
        motions = Motion.objects.filter(
            datetime__gte=start_time, datetime__lte=end_time,
            session__isnull=True,
        )
        print_method(f'{motions.count()} motions updated with session.')
        motions.update(session=session)
